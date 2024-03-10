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

## 프로젝트 세부내용

### 활용기술

| 데이터 수집 | Python, Airflow, AWS lambda |
| --- | --- |
| 데이터 적재 | AWS S3, Redshift |
| 데이터 시각화 | Preset |
| 인프라 | AWS EC2, Docker |
| 협업 도구 | Slack, Github, Gather, Notion |

### 프로젝트 아키텍처

![아키텍처_최종.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/b916e5ff-731f-492e-908c-9f62c6d3f824/4caa3f2c-7605-4f66-8ab5-d02428f04467/%E1%84%8B%E1%85%A1%E1%84%8F%E1%85%B5%E1%84%90%E1%85%A6%E1%86%A8%E1%84%8E%E1%85%A5_%E1%84%8E%E1%85%AC%E1%84%8C%E1%85%A9%E1%86%BC.png)

### DB 설계

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/b916e5ff-731f-492e-908c-9f62c6d3f824/baf6d879-0405-4b49-8b57-528c4d70bf74/Untitled.png)

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
