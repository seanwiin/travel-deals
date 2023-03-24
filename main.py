import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta, datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import cook_groups_food as c
import mysql.connector

#connection created
mydb = mysql.connector.connect(
  host="HOST_NAME",
  user="DB_USER",
  password="DB_PASS",
  database="DB_NAME"
)

mycursor = mydb.cursor()

groups = {

    'Travel': {
        'name': 'Travel',
        'webhook_footer': 'Discord Group',
        'color': 'ad6bff',
        'whop_url': 'https://whop.com/',
        'webhook_footer_img': 'webhook_img',
        'webhook': 'discord_webhook'},
}

def main():
    url = 'https://specialsalesdeals.com'

    deals_dict = []

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    main = soup.find_all('article')

    for i in main:
        today = date.today()
        today = today - timedelta(hours=8)
        date_updated = i.find(class_='date updated').text.strip()
        date_obj = datetime.strptime(date_updated, '%B %d, %Y').date()

        if date_obj == today:

            title = i.find(class_='entry-title').text.strip()
            dummy_title = title + ' - ' + str(date_obj)

            if dummy_title not in url_list:

                content2 = i.find(class_='entry-content')

                for p in content2.find_all('p'):
                    p.insert_after('\n')
                content = content2.text.strip()

                try:
                    entry_content = i.find('div', {'class': 'entry-content'})
                    a_tag = entry_content.find('a')
                    href = a_tag.get('href')
                except:
                    href = ''
                    pass

                deals_list = {
                    'text': content,
                    'title': title,
                    'href': href,
                    'dummy_title': dummy_title,
                    'created_at': today,
                }

                deals_dict.append(deals_list)
                sql_insert = "INSERT INTO special_sales (title, dummy_title, created_at) VALUES (%s, %s, %s)"
                sql_values = (deals_list['title'], deals_list['dummy_title'], deals_list['created_at'])
                mycursor.execute(sql_insert, sql_values)

    deals_df = pd.DataFrame(deals_dict)

    if len(deals_df) == 0:
        print('No Deals')
        # return 0
    else:
        for i in range(0, len(deals_df)):
            for z in groups.values():
                name = z['name']
                webhook_footer = z['webhook_footer']
                color = z['color']
                whop_url = z['whop_url']
                webhook_footer_img = z['webhook_footer_img']
                webhook = z['webhook']

                text = deals_df['text'][i]
                title = deals_df['title'][i]
                href = deals_df['href'][i]

                if href == '':
                    webhook_name = DiscordWebhook(url=webhook, username=name)
                    embed = DiscordEmbed(title="New Food Promotion Posted - {}!".format(title),description='{}'.format(text), color=color)
                    embed.set_footer(text=webhook_footer, icon_url=webhook_footer_img)
                    embed.set_thumbnail(url=webhook_footer_img)
                    embed.set_timestamp()
                    webhook_name.add_embed(embed)
                    response = webhook_name.execute(remove_embeds=True)
                else:
                    webhook_name = DiscordWebhook(url=webhook, username=name)

                    embed = DiscordEmbed(title="New Food Promotion Posted - {}!".format(title),description='{}'.format(text), color=color)
                    embed.add_embed_field(name='Link', value='{}'.format(href), inline=False)
                    embed.set_footer(text=webhook_footer, icon_url=webhook_footer_img)
                    embed.set_thumbnail(url=webhook_footer_img)
                    embed.set_timestamp()
                    webhook_name.add_embed(embed)
                    response = webhook_name.execute(remove_embeds=True)
                time.sleep(1)

mycursor.execute("SELECT distinct dummy_title FROM DB_NAME")

myresult = mycursor.fetchall()

url_list = []

for item in myresult:
    url = item[0]

    url_list.append(url)

main()

# conn.commit()
mydb.commit()
