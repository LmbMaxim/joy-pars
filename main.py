import argparse
import os
import re

from playwright.sync_api import sync_playwright
import wget



# Get page url from command line 
parser = argparse.ArgumentParser()
parser.add_argument(
        "-get"
        )


url = parser.parse_args()
URL = url.get


def nice_title(title):
    title_full = title.split(' ')
    title_args = title_full[0:-3]

    nice_title = ''
    for i in title_args:
        nice_title += f' {i}'
    
    return nice_title


def create_dir(title):
    if os.path.exists(title) == False:
        os.mkdir(title)


# Shoud cut junk from 'src' and return valid link
def find_ep_link(ep_links):
    def cut_start(ep_links):
        return str(ep_links.split('[1080p]')[1])

    def final_cut(ep_links):
        return(cut_start(ep_links).split(',')[0])
    

    return f'{final_cut(ep_links)}'



def player_name_and_id(page):
    prefered_order = ['Наш плеер', 'AllVideo', 'Sibnet']
    players_list = {}
    data = page.locator('[class="playlists-lists"] >> li').all()
    for player in data:
        player_name  = player.inner_text()
        player_id = player.get_attribute('data-id')
        players_list.update({player_name:player_id})

    x = 0 
    for x in prefered_order:
        if x in players_list:
            break
    
    return x, players_list.get(x)

        

def collect_ep_links(eps, player_name):
        ep_links_all = []
        for ep in eps:
            ep_num = ep.inner_text()
            ep_link_args = ep.get_attribute('data-file')


            if player_name == 'Наш плеер':
                ep_link = find_ep_link(ep_link_args)
            else:
                ep_link = ep_link_args

            print(ep_link)
            ep_links_all.append(ep_link)

        return ep_links_all


def create_art(page, path):
    path = f'{path}/000Art.png'
    page.locator('picture >> img').screenshot(path=path)


def main(url):
    with sync_playwright() as p:

        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        player = player_name_and_id(page)
        player_name = player[0]
        player_id = player[1]

        title = page.locator("[property='og:title']").get_attribute('content')[0:-8]
        eps = page.locator(f"[class='playlists-videos'] >> [data-id='{player_id}']").all()


        create_dir(title)
        create_art(page, title)

        ep_links_all = collect_ep_links(eps, player_name)
        
        i = 0
        for link in ep_links_all:
            n = str(i).zfill(2)
            path = f'{title}/{n}.mp4'
            if os.path.exists(path) == False:
                wget.download(link, path)
                i += 1

        browser.close()


main(URL)




