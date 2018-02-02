from django.shortcuts import render, redirect
from dwapi import datawiz
import datetime
import json
import pandas as pd
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from prod_stat.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from hashlib import sha1
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError


dw = False

# shops = [641, 595, 9366, 601, 3403, 3404],
@login_required(login_url='/login/')
def market(request, shop_id):
    global dw
    print(dw)
    if not dw:
        return redirect('/login')
    myd = {}
    # dw = datawiz.DW("test1@mail.com", "1qaz")
    b = dw.get_products_sale(by='turnover',
                             shops=[shop_id],
                             interval=datawiz.WEEKS).sum(axis=1)
    bb = dw.get_products_sale(by='qty',
                              shops=[shop_id],
                              interval=datawiz.WEEKS).sum(axis=1)
    rec_count = dw.get_products_sale(by='receipts_qty',
                                     shops=[shop_id],
                                     interval=datawiz.WEEKS).sum(axis=1)
    profit = dw.get_products_sale(by='profit',
                                  shops=[shop_id],
                                  interval=datawiz.WEEKS).sum(axis=1)

    n_prof = profit / rec_count  # profit / rec_count

    test = pd.concat([b, bb, rec_count, n_prof], axis=1).transpose()

    l_df = []
    for i in range(len(test.keys())):
        if len(test.keys()) == 1:
            break
        t_df = test.iloc[:, 0:2]
        test.drop(test.columns[0], axis=1, inplace=True)

        m_diff = t_df.diff(axis=1).dropna(axis=1, how='all')
        m_diff_v = (m_diff * 100 / t_df).dropna(axis=1, how='all')
        res = pd.concat([t_df, m_diff_v, m_diff], axis=1, join='inner').rename(
            {0: 'Оборот', 1: 'К-сть товарів', 2: 'К-сть чеків', 3: 'Середній чек'}, axis=0).dropna(axis=1, how='all')

        res_a = res, zip(res.index, res.values)
        l_df.append(res_a)

    myd['l_df'] = l_df

    # [641, 595, 9366, 601, 3403, 3404]
    shop_turn = dw.get_products_sale(shops=[641], view_type='represent', by='turnover',
                                     interval=datawiz.WEEKS)  # оборот
    shop_sales = dw.get_products_sale(shops=[641], view_type='represent', by='qty',
                                      interval=datawiz.WEEKS)  # кількість проданих товарів
    shop_info_l = []
    for i in range(len(shop_turn.index)):
        if i + 1 >= len(shop_turn.index):
            break
        a = shop_turn.iloc[i].sub(shop_turn.iloc[i + 1], axis=0)
        b = shop_sales.iloc[i].sub(shop_sales.iloc[i + 1], axis=0)
        c = pd.concat([a, b], axis=1, join='inner').rename({0: 'Зміна кількості ​​продаж', 1: 'Зміна обороту'}, axis=0)
        c_p = c[(c >= 0).all(axis=1)].sort_values(by=[0], ascending=False)
        c_n = c[(c < 0).all(axis=1)].sort_values(by=[0], ascending=True)
        to_date = shop_turn.index[i], shop_turn.index[i + 1]
        res_p = to_date, zip(c_p.index, c_p.values), 1
        res_n = to_date, zip(c_n.index, c_n.values), 0
        shop_info_l.append(res_p)
        shop_info_l.append(res_n)

    myd['shop_info'] = shop_info_l
    myd['shop_id'] = shop_id

    return render(request, 'prod_stat/shop.html', myd)


@login_required(login_url='/login/')
def main(request):
    # if not request.user.is_authenticated:
    #     return redirect('/login')
    global dw
    print(dw)
    myd = {}
    if dw:
        # dw = datawiz.DW("test1@mail.com", "1qaz")
        client_info = dw.get_client_info()
        myd['client_info'] = client_info
    return render(request, 'prod_stat/main.html', myd)


def vlogin(request):
    if request.user.is_authenticated:
        return redirect('/')

    myd = {}
    myd['form'] = LoginForm()

    if request.POST :
        u_name = request.POST['user_name']
        u_pass = request.POST['user_pass']

        try:
            global dw
            dw = datawiz.DW(u_name, u_pass)
            print(dw)
        except InvalidGrantError as e:
            print(e)
            myd['error'] = "введіть коректний ключ/cекрет"
            myd['form'] = LoginForm(request.POST)

        if dw:
            user = authenticate(request, username=u_name, password=u_pass)

            if user is not None:
                login(request, user)
                return redirect('/main')
            else:
                myd['form'] = LoginForm(request.POST)

    return render(request, 'prod_stat/login.html', myd)


def vlogout(request):
    logout(request)
    return redirect('/login')
