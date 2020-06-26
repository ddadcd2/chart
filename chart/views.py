from django.shortcuts import render
from .models import Passenger
from django.db.models import Count, Q
import json
from django.http import JsonResponse


def home(request):
    return render(request, 'chart/home.html')


def dual_axes():
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
        .order_by('ticket_class')

    # 빈 리스트 4종 준비 (series 이름 뒤에 '_data' 추가)
    categories = list()  # for xAxis
    survived_series_data = list()  # for series named 'Survived'
    not_survived_series_data = list()  # for series named 'Not survived'
    survived_rate_data = list()  # 생존율 리스트

    # 리스트 4종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])  # for xAxis
        survived_series_data.append(entry['survived_count'])  # for series named 'Survived'
        not_survived_series_data.append(entry['not_survived_count'])  # for series named 'Not survived'
        survived_rate_data.append(
            entry['survived_count'] / (entry['survived_count'] + entry['not_survived_count']) * 100)

    survived_series = {
        'name': '생존',
        'yAxis': 1,
        'data': survived_series_data,
        'type': 'column',
        'color': 'green',
        'tooltip': {'valueSuffix': '명'}
    }
    not_survived_series = {
        'name': '비 생존',
        'yAxis': 1,
        'data': not_survived_series_data,
        'type': 'column',
        'color': 'red',
        'tooltip': {'valueSuffix': '명'}
    }

    survived_rate = {
        'name': '생존율',
        'data': survived_rate_data,
        'type': 'spline',
        'tooltip': {'valueSuffix': '%'}
    }

    chart = {
        'chart': {'zoomType': 'xy'},
        'title': {'text': '좌석 등급에 따른 타이타닉 생존/비 생존 인원 및 생존율'},
        'xAxis': {'categories': categories},
        # 생존율 y
        'yAxis': [
            {'labels':
                 {'format': '{value}%', 'style': {'color': 'blue'}},
             'title':
                 {'text': '생존율', 'style': {'color': 'blue'}},
             },
            {'labels':
                 {'format': '{value}명', 'style': {'color': 'black'}},
             'title':
                 {'text': '인원', 'style': {'color': 'black'}},
             'opposite': 'true'
             }],
        'series': [survived_series, not_survived_series, survived_rate],
        'tooltip': {"shared": "true"}
    }
    dump = json.dumps(chart)
    return dump


def ticket_class_view_3(request):  # 방법 3

    return render(request, 'chart/ticket_class_3.html', {'chart': dual_axes()})



import pandas as pd
import matplotlib.pyplot as plt
import arrow


def confirmed():
    # 데이터 선별 및 로딩
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',parse_dates=['Date'])
    countries = ['Korea, South', 'Brazil', 'Italy', 'US', 'Canada']
    df = df[df['Country'].isin(countries)]

    # 데이터 구축하기
    df = df.pivot(index='Date', columns='Country', values='Confirmed')

    # countries 리스트 생성
    countries = list(df.columns)

    # df.reset_index()를 통하여 기존 인덱스 열을 데이터 열로 변경
    covid = df.reset_index('Date')

    # covid 인덱스와 columns를 새로 지정
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries

    # 인구 대비 건수 계산 (건/백만 명)
    populations = {'Korea, South':51269185, 'Brazil': 212559417 , 'Italy': 60461826 , 'US': 331002651, 'Canada': 37742154}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    # Section 6 - Generating Colours and Style
    colors = {'Korea, South': '#FFCD12', 'Brazil': '#5CD1E5', 'Italy': '#ABF200', 'US': '#6B66FF', 'Canada': '#000000'}
    plt.style.use('fivethirtyeight')

    # 타임스탬프 구하기
    date = covid.index
    my_arrow = list()

    for i in date:
        my_arrow.append([arrow.get(i.year, i.month, i.day).timestamp * 1000,
                           round(percapita.loc[i][country], 1)])   # 소수점 처리

    # 사전 생성하여 리스트에 삽입하기
    country_list = list()
    country_dict = dict()
    country_dict['country'] = country
    country_dict['date'] = my_arrow
    country_list.append(country_dict)

    # 차트
    chart = {
        'chart': {'type': 'spline'},
        'title': {'text': 'COVID-19 확진자 발생률'},
        'subtitle': {'text': 'Source: Johns Hopkins University Center for Systems Science and Engineering'},
        'xAxis': {'type': 'datetime'},
        'yAxis': [{
            'labels': {
                'format': '{value} 건/백만 명'
            }, 'title': {
                'text': '합계 건수'
                },
            }],
        'series': list(map(
                    lambda row: {'name': row['country'], 'data': row['date']}, country_list)
        ),
    }

    dump = json.dumps(chart)
    return dump


def covid_confirmed(request):
    return render(request, 'chart/covid_confirmed.html', {'chart': confirmed()})



# COVID19 - recovered
def recovered():
    pass
    # 데이터 선별 및 로딩
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',parse_dates=['Date'])
    countries = ['Korea, South', 'Brazil', 'Italy', 'US', 'Canada']
    df = df[df['Country'].isin(countries)]

    # 데이터 구축하기
    df = df.pivot(index='Date', columns='Country', values='Recovered')

    # countries 리스트 생성
    countries = list(df.columns)

    # df.reset_index()를 통하여 기존 인덱스 열을 데이터 열로 변경
    covid = df.reset_index('Date')

    # covid 인덱스와 columns를 새로 지정
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries

    # 인구 대비 건수 계산 (건/백만명)
    populations = {'Korea, South':51269185, 'Brazil': 212559417 , 'Italy': 60461826 , 'US': 331002651, 'Canada': 37742154}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    # Section 6 - Generating Colours and Style
    colors = {'Korea, South': '#FFCD12', 'Brazil': '#5CD1E5', 'Italy': '#ABF200', 'US': '#6B66FF', 'Canada': '#000000'}
    plt.style.use('fivethirtyeight')

    # 타임스탬프 구하기
    date = covid.index
    my_arrow = list()

    for i in date:
        my_arrow.append([arrow.get(i.year, i.month, i.day).timestamp * 1000,
                           round(percapita.loc[i][country], 1)])   # 소수점 처리

    # 사전 생성하여 리스트에 삽입하기
    country_list = list()
    country_dict = dict()
    country_dict['country'] = country
    country_dict['date'] = my_arrow
    country_list.append(country_dict)

    # 차트
    chart = {
        'chart': {'type': 'spline'},
        'title': {'text': 'COVID-19 회복자 발생률'},
        'subtitle': {'text': 'Source: Johns Hopkins University Center for Systems Science and Engineering'},
        'xAxis': {'type': 'datetime'},
        'yAxis': [{
            'labels': {
                'format': '{value} 건/백만 명'
            }, 'title': {
                'text': '합계 건수'
                },
            }],
        'series': list(map(
                    lambda row: {'name': row['country'], 'data': row['date']}, country_list)
        ),
    }

    dump = json.dumps(chart)
    return dump


def covid_recovered(request):
    return render(request, 'chart/covid_recovered.html', {'chart': recovered()})




# COVID19 - deaths
def deaths():
    pass
    # 데이터 선별 및 로딩
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',parse_dates=['Date'])
    countries = ['Korea, South', 'Brazil', 'Italy', 'US', 'Canada']
    df = df[df['Country'].isin(countries)]

    # 데이터 구축하기
    df = df.pivot(index='Date', columns='Country', values='Deaths')

    # countries 리스트 생성
    countries = list(df.columns)

    # df.reset_index()를 통하여 기존 인덱스 열을 데이터 열로 변경
    covid = df.reset_index('Date')

    # covid 인덱스와 columns를 새로 지정
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries

    # 인구 대비 건수 계산 (건/백만명)
    populations = {'Korea, South':51269185, 'Brazil': 212559417 , 'Italy': 60461826 , 'US': 331002651, 'Canada': 37742154}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    # Section 6 - Generating Colours and Style
    colors = {'Korea, South': '#FFCD12', 'Brazil': '#5CD1E5', 'Italy': '#ABF200', 'US': '#6B66FF', 'Canada': '#000000'}
    plt.style.use('fivethirtyeight')

    # 타임스탬프 구하기
    date = covid.index
    my_arrow = list()

    for i in date:
        my_arrow.append([arrow.get(i.year, i.month, i.day).timestamp * 1000,
                           round(percapita.loc[i][country], 1)])   # 소수점 처리

    # 사전 생성하여 리스트에 삽입하기
    country_list = list()
    country_dict = dict()
    country_dict['country'] = country
    country_dict['date'] = my_arrow
    country_list.append(country_dict)

    # 차트
    chart = {
        'chart': {'type': 'spline'},
        'title': {'text': 'COVID-19 사망자 발생률'},
        'subtitle': {'text': 'Source: Johns Hopkins University Center for Systems Science and Engineering'},
        'xAxis': {'type': 'datetime'},
        'yAxis': [{
            'labels': {
                'format': '{value} 건/백만 명'
            }, 'title': {
                'text': '합계 건수'
                },
            }],
        'series': list(map(
                    lambda row: {'name': row['country'], 'data': row['date']}, country_list)
        ),
    }

    dump = json.dumps(chart)
    return dump


def covid_deaths(request):  # 방법 3
    return render(request, 'chart/covid_deaths.html', {'chart': deaths()})




