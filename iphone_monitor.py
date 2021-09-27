import requests as req
import bs4
import json
import time
import os
from datetime import datetime


def get_json_page(url):
    j_page=req.get(url)
    if j_page.status_code==200:
        return json.loads(j_page.content),j_page.status_code
    else:
        return {},j_page.status_code

def get_page_requests(url):
    page=req.get(url)
    return bs4.BeautifulSoup(page.content,'lxml')


def get_userdetails():
    with open('userdetails.txt','r') as f:
        sri=f.read()
        l1=sri.split('\n')
        l1=[i.split(':')[1] for i in l1]
        return l1[0],l1[1],l1[2],int(l1[3]),l1[4],l1[5],l1[6],l1[7]

def get_models_name():
    models_page=get_page_requests('https://www.apple.com/hk/shop/buy-iphone')
    m_phone=models_page.find('div',attrs={'class':'rf-cards-scroller-platter'})
    p_links={}
    for i in m_phone.find_all('a'):
        if 'iphone' in str(i['href'].split('/')[-1]):
            name_model=str(i['href'].split('/')[-1])
            if name_model=='iphone-se':
                p_links[name_model]='https://www.apple.com/hk/shop/product-locator-meta?family='+''.join(name_model.split('-'))+'2'
            else:
                p_links[name_model]='https://www.apple.com/hk/shop/product-locator-meta?family='+''.join(name_model.split('-'))

    return p_links

def search_modelnum_link(url,model_num):
    q1,status=get_json_page(url)
    t1=q1['body']['productLocatorOverlayData']['productLocatorMeta']['products']
    product=''
    for i in t1:
        if i['partNumber']==model_num:
            product=i['productLink']
            break
    return product

def monitor_model_available(model_num):
    url="https://www.apple.com//hk/shop/retail/pickup-message?pl=true&parts.0={}&location=hongkong".format(model_num)
    q1,status=get_json_page(url)
    print(status)
    stores={}
    if status==503:
        time.sleep(7)
        sorted_dict={}
    else:
        for i in q1['body']['stores']:
          if i['partsAvailability'][model_num]['storeSelectionEnabled']:
            stores[int(i['storeNumber'][1:])]={'storeName':i['storeName'],'city':i['city'],'storeSelectionEnabled':i['partsAvailability'][model_num]['storeSelectionEnabled']}
        sorted_dict = dict(sorted(stores.items()))
    return sorted_dict

def model_link_for_purchase(model_num):
    d1=get_models_name()
    mlink={}
    for i in list(d1.values()):
        # print(i)
        p=search_modelnum_link(i,model_num)
        if len(p)!=0:
          mlink[model_num]=p
          break 
    return mlink

def search_model_nuber(model_num,my_date):
    while True:
        CurrentDate = datetime.now()
        if CurrentDate > my_date:
            print("Timeline Complete & Nothing Found!!")
            os._exit(0)
        else:

            c = my_date - CurrentDate
            dict_stores=monitor_model_available(model_num)
            time.sleep(2)
            if len(dict_stores)==0:
                print('Not Avaliable this Model',model_num)
                dict_stores={}
                print("Remaining Time :", str(c)[:-10],'minutes')
                continue
            else:
                link=model_link_for_purchase(model_num)
                print(link)
                print(dict_stores)
                break


    return link,dict_stores


def user_input_data():
    # try:
    all_data=[]
    print("%%%%%%%%%   Personal Information   %%%%%%%%%%")
    if os.path.isfile('userdetails.txt'):
      status=input('Do you want to use previous details (y or n) :')
      if status=='y':
          u_name,l_name,u_email,cardnum,cvv,expire,iphone_gift,add=get_userdetails()
          all_data.append([u_name,l_name,u_email,cardnum,expire,cvv,iphone_gift,add])
      else:
          u_name=input('Enter your First Name :')
          l_name=input('Enter your Last Name :')
          u_email=input('Enter Email :')
          cardnum=input('Enter Card Number :')
          cvv=input("Enter Last 3 Numbers :")
          mexpire=input("Enter Expire date (MM):")
          yexpire=input("Enter Expire date (YY):")
          expire=mexpire+yexpire
          iphone_gift=input("Enter iphone gift Code :")
          add=input("Enter Address :")
          all_data.append([u_name,l_name,u_email,cardnum,expire,cvv,iphone_gift,add])
    else:
      u_name=input('Enter your First Name :')
      l_name=input('Enter your Last Name :')
      u_email=input('Enter Email :')
      cardnum=input('Enter Card Number :')
      cvv=input("Enter Last 3 Numbers :")
      mexpire=input("Enter Expire date (MM):")
      yexpire=input("Enter Expire date (YY):")
      expire=mexpire+yexpire
      iphone_gift = input("Enter iphone gift Code :")
      add=input("Enter Address :")
      all_data.append([u_name,l_name,u_email,cardnum,expire,cvv,iphone_gift,add])

      qsave=input("Do you want to save Details for Future purchase (y or n) :")
      if qsave=='y':
          with open('userdetails.txt','w') as f:
              f.write('First Name :'+u_name+'\n'+'Last Name :'+l_name+'\n'+'Email :'+u_email+'\n'+'Card Number :'+str(cardnum)+'\n'+'CVV :'+str(cvv)+'\n'+'Expire Date :'+str(expire)+'\n'+'iPhone Gift Code :'+iphone_gift+'\n'+'Address :'+add)
    print("\n%%%%%%%%%   Mobile Detail   %%%%%%%%%%%")
    model_num=input("Enter Model Number :")
    num=input('How many number of Mobile want to Buy :')
    slot=input("Enter Avaliable Time Window Slot Number :")
    if (len(str(all_data[0][3]))!=0) and (len(str(all_data[0][6]))!=0):
        pay_check = input("Enter Payment Method (1 for Credit Card & 2 for iPhone Gift) :")
    elif (len(str(all_data[0][3]))!=0) and (len(str(all_data[0][6]))==0):
        pay_check=1
    elif (len(str(all_data[0][3]))==0) and (len(str(all_data[0][6]))!=0):
        pay_check=2
    else:
        print("Please Enter Credit card details first")
        return 0
    try:
        my_string = str(input('Enter date(yyyy-mm-dd hh:mm): '))
        my_date = datetime.strptime(my_string, "%Y-%m-%d %H:%M")
    except:
        print('Invalied DateTime!!!!\n Please try Again')
        os._exit(0)
    all_data[0].insert(0,num)
    all_data[0].append(slot)

    link,stores=search_model_nuber(model_num,my_date)
    for i in stores:
      all_data[0].append(stores[i]['city'])
      break
    all_data[0].append(int(pay_check))
    all_data[0].insert(0,link[model_num])
    return all_data
    # except:
    #     print("Invalied Input Please enter Number")

if __name__=="__main__":
    print(user_input_data())


