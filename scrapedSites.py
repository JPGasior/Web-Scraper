from bs4 import BeautifulSoup
import requests
import time
import csv
from selenium import webdriver
import re


def lowes_kitchen_scrape(link):
    base_link = 'https://www.lowes.ca'
    counter = 0
    p_type = 'Faucet'
    sub_type = 'Kitchen'
    store = "Lowe's Canada"
    sector = 'Residential'
    full_data = list()

    more_pages = True # always run through while loop at least once
    while (more_pages == True):
        r = requests.get(link)
        if r.status_code != 200:
            return 'Website not available'

        c = r.content;

        soup = BeautifulSoup(c, 'lxml')

        # check if there are more pages of product. If there are, get the link to the next page which passes to soup
        mp = soup.find('div', {'id': 'divBtnPageBtm'})
        if 'Next' in mp.text:
            more_pages = True
            nl = mp.find('a', href=True,class_=['next']) # next link
            link = base_link + nl['href']
        else:
            more_pages = False

        # loop through all products on page
        for div in soup.find_all('div', class_= ['g5']) and soup.find_all('div', class_= ['comidx']):
            counter += 1

            # initialize/reset some variables
            customer_no = ''
            p_model = ''
            marketing_desc = ''
            features = []
            p_collection = ''

            # get product title
            p_title = div.select_one('span[id*=catTitle]').text.strip()

            # get company name
            p_brand = div.select_one('span[id*=catBrand]').text.strip()

            # get model no
            for pm in div.find_all('div', class_=['fnts']):
                if pm:
                    if 'Model:' in pm.text:
                        p_model = pm.text.strip('Model: ')
                    if "Lowe's Item #:" in pm.text:
                        customer_no = pm.text.strip("Lowe's Item #: ")

            # get image link
            p_img = div.find('img')['src']

            # get product link
            pl = div.find('a', href=True)
            prod_link = base_link + pl['href']

            # -----------------------------------------------------
            # now go into each product page and pull more info
            product_r = requests.get(prod_link)
            product_c = product_r.content

            product_soup = BeautifulSoup(product_c, 'lxml')

            # get collection
            for d in product_soup.find_all('div', class_="fnts l hiddens"):
                if 'Collection' in d.text:
                    col = d.select_one('a')
                    p_collection = col.text

            # get marketing description
            md = product_soup.find(id='prodDesc')
            if md.p:
                md2 = md.select('p')
                if len(md2) > 1:
                    md3 = md2[1].text
                    marketing_desc = md3
                    if 'Specifications' in md3:
                        marketing_desc = ''

            # get price
            price = product_soup.find('div', id='divPrice').text.strip()

            # get features
            if md.find('li'):
                for li in md.find_all('li'):
                    features.append(li.text)
            # add data to a list to signify a row
            product_data = [p_title, p_brand, p_type, sub_type, marketing_desc, p_model, features, price, customer_no, p_collection,
                           prod_link, p_img, store, sector]

            # add row of product data to the end of the "master" data list
            full_data.append(product_data)

            print(counter, store, p_brand, p_title)


    print('Found items:', counter, 'in', store, 'for', p_type, sub_type)

    return full_data

def rona_kitchen_scrape(link):
    #   function to grab kitchen faucet data from canadian tire
    base_link = 'https://www.rona.ca'
    counter = 0
    more_pages = True
    p_type = 'Faucet'
    sub_type = 'Kitchen'
    store = "Rona Canada"
    sector = 'Residential'
    full_data = list()


    while more_pages == True:
        r = requests.get(link)
        if r.status_code != 200:
            print('Rona website not available')
            return

        c = r.content

        soup = BeautifulSoup(c, 'lxml')

        mp = soup.find('div', class_='pagination')
        if 'next' in mp.text:
            more_pages = True
            nl = mp.find('a', href=True,class_= "pagination__button-arrow pagination__button-arrow--next") # next link
            link = base_link + nl['href']
        else:
            more_pages = False

    #   loop through all products on page
        for div in soup.find_all('div', class_="col-lg-3 col-md-4 col-sm-4 col-xs-6"):
            counter += 1

            # initialize some variables
            customer_no = ''
            p_model = ''
            marketing_desc = ''
            features = []
            p_collection = ''

            spec = ''
            value = ''

            # get brand/manufacturer
            p_brand = div.find('div', class_="product-tile__brand").text

            # get product description/title
            p_title = div.find('a', class_="product-tile__title productLink").text

            # find link to get to product page
            pl = div.find('a', href=True, class_="product-tile__image-link productLink")
            prod_link = pl['href']

            # get image link too
            p_img = pl.find('img')['src']

            # -----------------------------------------------------
            # now go into each product page and pull more info
            product_r = requests.get(prod_link)
            product_c = product_r.content

            product_soup = BeautifulSoup(product_c, 'lxml')

            d = product_soup.find('div', class_="page-product__sku-infos")
            if d:
                for s in d.find_all('span'):
                    if 'Model' in s.text:
                        p_model = s.text.strip('Model #')
                    if 'Item' in s.text:
                        customer_no = s.text.strip('Item #')

            # get price
            price = product_soup.find('div', class_="price-box__regularPrice").text

            # get marketing description
            m = product_soup.find('h2', class_="page-product__section-title")
            md = m.find_next_sibling('div')
            marketing_desc = md.text


            # get collection/family and features
            ft = product_soup.find('div', class_="row row--no-padding row--flex-full-height")
            if ft:
                for feat in ft.find_all('div', class_="col-sm-6 col-xs-12"):
                    sp = feat.find('div', class_="page-product__specs__name")
                    if sp:
                        spec = sp.text
                    val = feat.find('div', class_="page-product__specs__value")
                    if val:
                        value = val.text
                    if 'Model' in spec:
                        p_collection = value
                    if 'Collection' in spec:
                        p_collection = value

                    features.append(spec + ': ' + value)

            product_data = [p_title, p_brand, p_type, sub_type, marketing_desc, p_model, features, price,
                            customer_no, p_collection,
                            prod_link, p_img, store, sector]

            # add row of product data to the end of the "master" data list
            full_data.append(product_data)

            print(counter, store, p_brand, p_title)

    print('Found items:', counter, 'in', store, 'for', p_type, sub_type)

    return full_data

def walmart_kitchen_scrape(link):
    base_link = 'https://www.walmart.ca'
    p_type = 'Faucet'
    sub_type = 'Kitchen'
    store = "Walmart Canada"
    sector = 'Residential'
    full_data = list()
    counter = 0

    more_pages = True


    # create a virtual web browser to allow javascript on walmart page to load properly

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    while more_pages == True:

        driver.get(link)

        counter += 1

        print(counter, link)

        c = driver.page_source

        soup = BeautifulSoup(c, 'lxml')

        mp = soup.find('a', {'id': 'loadmore'})
        if mp:
            more_pages = True
            link = base_link + mp['href']
        else:
            more_pages = False



    # be nice to the internet, quit the browser when you're done with it
    driver.quit()

def canadian_tire_kitchen_scrape(link):
    counter = 0

    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    driver = webdriver.Chrome()
    driver.implicitly_wait(30)

    driver.get(link)
    c = driver.page_source
    print('is this ok')
    soup = BeautifulSoup(c, 'lxml')

    # mp = soup.find('div', class_="parbase search-results-grid section")

    mp = soup.select('div', class_="parbase search-results-grid section")
    print(mp.prettify())

    while "display: block;" in str(soup):
        print('still good')
        driver.find_element_by_class_name("search-results-grid__load-more-results__link").click()
        c = driver.page_source
        soup = BeautifulSoup(c, 'lxml')
        if "display: none;" in str(soup):
            break



    # be nice and quit the web driver


    time.sleep(60)
    driver.quit()

def main():

    t1 = time.time() # time how long scrape takes

    # set up some variables
    lowes_kitchen = []
    rona_kitchen =[]
    walmart_kitchen = []
    ct_kitchen = []

    data = [['Product Title', 'Brand', 'Type', 'Sub Type', 'Marketing Description', 'Model No', 'Features', 'Price',
             'Customer PN', 'Collection/Family', 'Link', 'Image', 'Store', 'Sector']]

    url = 'https://www.lowes.ca/kitchen/kitchen-faucets/?perpage=80&p=1'
    lowes_kitchen = lowes_kitchen_scrape(url)
    data.extend(lowes_kitchen)

    url = 'https://www.rona.ca/webapp/wcs/stores/servlet/RonaAjaxCatalogSearchView?navDescriptors=1000039716&catalogId=10051&searchKey=RonaEN&langId=-1&keywords=faucets&storeId=10151&pageSize=80&content=Products&page=1'
    rona_kitchen = rona_kitchen_scrape(url)
    data.extend(rona_kitchen)

    # url = 'https://www.walmart.ca/en/home/sinks-faucets-vanities/kitchen-faucets/N-628'
    # walmart_kitchen = walmart_kitchen_scrape(url)
    # data.extend(walmart_kitchen)

    # url = 'https://www.canadiantire.ca/content/canadian-tire/en/tools-hardware/plumbing/faucets-fixtures/kitchen-faucets.html?adlocation=LIT_Category_Product_KitchenFaucetsCat_en'
    # ct_kitchen = canadian_tire_kitchen_scrape(url)
    # data.extend(ct_kitchen)

    # write out data to csv
    with open('db.csv', 'w', newline='', encoding='utf-8') as fileOut:
        wr = csv.writer(fileOut)
        wr.writerows(data)

    t2 = time.time()
    t = (t2-t1).__round__(2)
    print(f'This took {t} seconds')

if __name__ == '__main__':
    main()