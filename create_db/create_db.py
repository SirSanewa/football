from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from db import engine
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


def use_and_switch_to_club_page(club, link_name: str, driver):
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


def data_mining(driver):
    """
    Main function providing flow to the app.
    :param driver:
    :return:
    """
    driver.get("https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1")
    accept_cookies(driver)

    # iterate over club rows
    clubs_table = driver.find_element_by_css_selector("#yw1 > table > tbody")

    # get driver main window name
    window_before = driver.window_handles[0]
    for club_id, club in enumerate(clubs_table.find_elements_by_xpath("./tr"), start=1):
        link_club_name = get_club_link_name(club)
        use_and_switch_to_club_page(club, link_club_name, driver)

        full_club_name = driver.find_element_by_css_selector(
            "#verein_head > div > div.dataHeader.dataExtended > div.dataMain > div > div.dataName > h1 > span").text
        print(club_id, full_club_name, " :")

        players_table = driver.find_element_by_xpath("//*[@id='yw1']/table/tbody")
        for player in players_table.find_elements_by_xpath("./tr"):
            player_name, player_position, player_shirt, player_dob, player_value = player_data(player)
            print(f"   - name = {player_name}, shirt nr = {player_shirt}, position = {player_position}, dob = {player_dob}, value = {player_value}")

        driver.close()
        driver.switch_to.window(window_before)


if __name__ == "__main__":
    web_driver = webdriver.Chrome(ChromeDriverManager().install())
    data_mining(web_driver)

    Base.metadata.create_all(engine, checkfirst=True)
