# 교통사고 현황 분석

## 프로젝트 개요

본 프로젝트는 교통사고 데이터와 날씨 데이터를 수집하여 함께 분석하고 시각화하는 대시보드를 구현하는 것을 목표로 합니다. 이를 통해 교통사고의 발생과 날씨 상황 간의 상관관계를 분석하고 시민들에게 유용한 정보를 제공합니다.

### 주제 선정 이유

- 실시간 데이터의 부재 : 교통사고 데이터가 보통 6개월마다 업데이트되어 최근 교통사고 데이터에 접근하는 데 시간이 많이 소요되는 문제가 있습니다. 이에 대응하여 교통사고 데이터에 실시간으로 접근할 수 있는 시스템을 구축하기로 했습니다. 이를 통해 신속한 사고 패턴 파악과 예방 조치를 취할 수 있어 도로 안전성을 높이고자 합니다.
- 교통사고와 날씨 상황 간의 관계: 교통사고는 날씨 조건에 따라 영향을 받는 경우가 많습니다. 이러한 관계를 분석하여 시민들에게 유용한 정보를 제공하고자 해당 주제를 선정하였습니다.
- 시민 복지 증진: 교통사고 예방 및 안전 운전을 돕기 위해 날씨 상황과의 관련성을 시각적으로 전달할 수 있는 대시보드를 구현하고자 하였습니다.

### 프로젝트 목표

- AWS 인프라 구축 경험
- Open API 를 통한 실시간 데이터 수집 경험
- AWS Lambda 및 Airflow Dag를 통한 ETL, ELT 경험
- CI/CD 구축 경험

## 활용기술

### 데이터 수집

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900?style=for-the-badge&logo=AWS%20Lambda&logoColor=black)             


### 데이터 적재
![amazons3](https://img.shields.io/badge/amazon%20s3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![amazonredshift](https://img.shields.io/badge/amazon%20redshift-8C4FFF?style=for-the-badge&logo=amazonredshift&logoColor=ffffff)

### 인프라
![amazonec2](https://img.shields.io/badge/amazon%20ec2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=000000)
![docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=ffffff)

### 데이터 시각화
![preset](https://img.shields.io/badge/preset-1BB3A4?style=for-the-badge&logo=preset&logoColor=61DAFB)


### 협업 도구
![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=Slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Gathertown](https://img.shields.io/badge/Gather%20town-017CEE?style=for-the-badge&logo=gathertown&logoColor=white)

## 프로젝트 세부내용

### 프로젝트 아키텍처
![image](https://github.com/DE-proj3-1/traffic-accident-project/assets/51227226/cd52fc00-31d8-42a3-8648-07126b3dbf0a)

### ERD
![image](https://github.com/DE-proj3-1/traffic-accident-project/assets/51227226/bd169129-a9aa-46ec-a53c-c6502c8ce2ab)


### 데이터 파이프라인

**수집 데이터**

- [서울시 실시간 돌발정보 API](https://data.seoul.go.kr/dataList/OA-13315/A/1/datasetView.do)
- [실시간 날씨 API](https://www.data.go.kr/data/15084084/openapi.do)
- 교통사고정보 개방시스템
    - [결빙 사고다발지역정보 API](https://opendata.koroad.or.kr/api/selectFreezingDataSet.do;jsessionid=0020728C779AF1B1769A0F4CBEC093A3)
        - 대상사고 : 최근 5년간 11월~3월 중 발생한 노면상태가 서리/결빙인 교통사고
        - 다발지역 선정조건 : 반경 200m내, 대상사고 3건 이상 발생지(사망사고 포함 시 2건 이상)
    - [연휴기간별 사고다발지역정보 API](https://opendata.koroad.or.kr/api/selectTmzonDataSet.do)
        - 대상사고 : 1년 중 설날, 추석, 여름휴가철, 4월봄철주말, 10월단풍철주말 등 연휴기간동안 발생한 교통사고
        - 다발지역 선정조건 : 반경 100m내, 대상사고 4건 이상 발생지
    - [사망교통사고정보 API](https://opendata.koroad.or.kr/api/selectDeathDataSet.do)
        - 교통사고 일시 부터 30일이내 사망한경우를 사망교통사고라 정의하고 사고정보를 선택한 조건에 따라 json/xml형식으로 제공합니다.
     
### 최종 결과물
![image](https://github.com/DE-proj3-1/traffic-accident-project/assets/51227226/d7e3d824-9021-4b4b-979b-629204eb22c6)

### 팀원 소개 및 역할

| 이름 | 역할 | 깃허브 |
| --- | --- | --- |
| 최아정 | CI/CD, 데이터 수집, ERD, ETL, ELT, 대시보드 구성 | [@AJ15H](https://github.com/AJ15H) |
| 황예원 | 인프라 구성, 데이터 수집, ERD, ETL, ELT, DB 구축, 대시보드 구성  | [@wwyyww](https://github.com/wwyyww) |
