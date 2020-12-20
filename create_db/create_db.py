import urllib.request
import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from db import engine, create_session
from models.base import Base
from models.player import Player
from models.club import Club


def accept_cookies(driver):
    """
    Switch to pop up iframe to accept cookies and return back to default page.
    :param driver:
    :return:
    """
    iframe = driver.find_element_by_id("sp_message_iframe_382445")
    driver.switch_to.frame(iframe)
    driver.find_element_by_xpath("/html/body/div/div[3]/div[3]/div[2]/button").click()
    driver.switch_to.default_content()


def get_club_link_name(club_tr) -> str:
    """
    Takes in table row WebElement which text includes position, club name, player average age and total value
    and returns only club link name.
    :param club_tr:
    :return: str
    """
    row_text = club_tr.text.split()
    club_row = [word for word in row_text if word.isalpha()]
    return " ".join(club_row)


def use_link_and_switch_to_club_page(club, link_name: str, driver):
    """
    Takes in club row WebElement and for given club name clicks appropriate link.
    Switches driver focus to new  maximized window.
    :param club:
    :param link_name:
    :param driver:
    :return:
    """
    link = club.find_element_by_link_text(link_name)
    ActionChains(driver) \
        .move_to_element(link) \
        .key_down(Keys.SHIFT) \
        .click(link) \
        .key_up(Keys.SHIFT) \
        .perform()
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    driver.maximize_window()


def player_data(player_row) -> tuple:
    """
    Takes in player row WebElement, converts it to list and return player's full name, position, shirt number, dob and
    value as tuple.
    :param player_row:
    :return:
    """
    player_data_list = [cell.text for cell in player_row.find_elements_by_xpath("./td") if cell.text]
    player_name_position = player_data_list[1].split('\n')
    player_name = player_name_position[0].replace(".", "").replace("*", "")
    player_position = player_name_position[1]
    player_shirt = player_data_list[0]
    player_dob = player_data_list[2]
    player_value = player_data_list[3]
    return player_name, player_position, player_shirt, player_dob, player_value


def save_club_logo_to_file(driver):
    club_image_object = driver.find_element_by_css_selector("#verein_head > div > div > div.dataBild > img")
    image_src = club_image_object.get_attribute('src')
    urllib.request.urlretrieve(image_src, "temp/temp.png")


def create_new_db_club(driver, club_id):
    name_select = "#verein_head > div > div.dataHeader.dataExtended > div.dataMain > div > div.dataName > h1 > span"
    full_club_name = driver.find_element_by_css_selector(name_select).text
    with open("temp/temp.png", "rb") as file:
        club_image = bytearray(file.read())
        new_item = Club(club_id=club_id, club_name=full_club_name, club_logo=club_image)
    os.remove("temp/temp.png")
    db.add(new_item)
    db.commit()


def save_player_photo_to_file(driver, player_id):
    player_image_object = driver.find_element_by_xpath(
        f"//*[@id='yw1']/table/tbody/tr[{player_id}]/td[2]/table/tbody/tr[1]/td[1]/a/img")
    player_image_src = player_image_object.get_attribute('data-src')
    urllib.request.urlretrieve(player_image_src, "temp/temp.png")


def player_nationality(player):
    flag = player.find_element_by_class_name("flaggenrahmen")
    return flag.get_property("title")


def create_new_db_player(driver, club_id):
    player_name, player_position, player_shirt, player_dob, player_value = player_data(driver)
    nationality = player_nationality(driver)
    with open("temp/temp.png", "rb") as file:
        player_image = bytearray(file.read())
        new_item = Player(name=player_name,
                          photo=player_image,
                          dob=player_dob,
                          club_id=club_id,
                          shirt_number=player_shirt,
                          position=player_position,
                          nationality=nationality,
                          value=player_value
                          )
    os.remove("temp/temp.png")
    db.add(new_item)
    db.commit()


def data_mining(driver):
    """
    Main function providing flow to the app.
    :param driver:
    :return:
    """
    driver.get("https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1")
    accept_cookies(driver)

    # get driver main window name
    window_before = driver.window_handles[0]

    clubs_table = driver.find_element_by_css_selector("#yw1 > table > tbody")
    for club_id, club in enumerate(clubs_table.find_elements_by_xpath("./tr"), start=1):
        link_club_name = get_club_link_name(club)
        use_link_and_switch_to_club_page(club, link_club_name, driver)

        save_club_logo_to_file(driver)
        create_new_db_club(driver, club_id)

        players_table = driver.find_element_by_xpath("//*[@id='yw1']/table/tbody")
        for player_id, player in enumerate(players_table.find_elements_by_xpath("./tr"), start=1):
            save_player_photo_to_file(player, player_id)
            create_new_db_player(player, club_id)

        driver.close()
        driver.switch_to.window(window_before)


if __name__ == "__main__":
    Base.metadata.create_all(engine, checkfirst=True)
    db = create_session()

    web_driver = webdriver.Chrome(ChromeDriverManager().install())
    data_mining(web_driver)
