# -*- coding: utf-8 -*-

import time
import json
import requests
import logging
import pytz
from datetime import datetime, timezone
from tzlocal import get_localzone
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# bot info
bot_token = ''
bot = telegram.Bot(token=bot_token) # bot을 선언
# 토큰 집어넣어서 url 정의
bot_url = "https://api.telegram.org/bot{}/".format(bot_token)

# elderly info
elderly_id = ''
elderly_name = ''
elderly_preferred_time = [9, 19]

# receiver info
receiver_id = ''

# google spreadsheet
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('', scope)
client = gspread.authorize(creds)
sheet = client.open("log").sheet1

# morning converation info
morning_greeting = ["엄마 ! 내가 엄마 건강에 좋은 정보 하나 알아왔어~", "엄마 내가 오늘 새로운 뉴스 하나 발견했어", "엄마 내가 건강 정보 하나 봤는데 같이 볼래?",
                    "엄마 내가 뭐 보내줄게", "맘! 건강정보 하나 새로운거 보낼게 봐봐~", "엄마 이거 같이 보자~", "엄마 이거봐봐"]

morning_health_info = [
    "<컬러푸드1>\n\n몸에 좋고 맛도 좋은 컬러푸드는 항산화 작용을 하고 암 예방의 효과도 있다고 알려져 있습니다.\n오늘은 빨간색에 대해 알아볼게요 빨간색 음식 중에는 토마토가 대표적으로 항산화 작용과 암 예방 효과가 있습니다. 토마토 안에 함유된 라이코펜이라는 물질 덕분인데요,\n식후에도 과자같은 후식들 보다는 토마토를 먹는 것이 좋습니다.",
    "<단백질 결핍 방지2>\n\n고기를 섭취하지 않는 것이 건강식일까요? 아닙니다.\n적절한 동물성 단백질 섭취는 근육량과 면역력을 유지하는데 필수적인 만큼 기름기가 적은 살코기 육류로 단백질을 섭취하는 것이 좋습니다. 단백질은 저장이 되지 않는 영양소로 하루 먹는 총량도 중요하지만 끼니마다 부족하지 않게 섭취해야합니다.\n매 끼니에 손바닥 크기 3분의 1 정도의 기름기가 적은 살코기나, 닭고기, 생선, 두부, 콩류 중 하나를 섭취하셔야 합니다.",
    "<식품으로 우울증 문제 해결>\n\n마음의 감기'라고도 불리는 우울증은 정말 많은 사람이 인생에서 한 번 이상 겪는 정신과 질환이다. 우울증의 주된 원인으로 알려진 호르몬은 '세로토닌'이다. 세로토닌의 별명은 '행복 호르몬'으로, 이 호르몬 작용이 부족하면 우울증이 찾아오고, 덩달아 세로토닌에서 만들어지는 멜라토닌도 부족해 불면증도 찾아온다.\n그런데 세로토닌의 90%가 만들어지는 장소는 뇌가 아니라 장이다. 장 내벽에 있는 '엔테로크로마틴'이라는 세포가 세로토닌을 직접 합성하기 때문이다. 세로토닌은 트립토판이라는 아미노산으로부터 만들어진다. 세로토닌이 트립토판으로부터 만들어지려면 여러 가지 효소와 효소를 돕는 조효소들이 있어야 한다. 이 영양소들은 세로토닌뿐만 아니라 도파민, 노르에피네프린의 생성과정에도 관여한다. 도파민은 삶의 재미를 느끼게 해주고, 노르에피네프린 역시 우울증과 연관성을 가지는 신경전달물질이다.\n실제 한 연구에 따르면 니아신, 엽산 등의 조효소 역할을 하는 영양소가 부족하면 우울증약 복용 효과가 더디게 나타난다는 내용이 보고됐다. 약간의 우울감이 있다면 자신의 식단을 점검해보고 비타민, 미네랄이 풍부함 채소, 과일, 견과류를 섭취하는 것도 좋은 방법이다. 그중에서도 비타민 B12는 우울함을 없애고 기분을 북돋아 주는 영양소다. 국제신경정신약리학저널에도 비타민 B12가 우울감을 완화한다는 연구가 실렸다.",
    "<컬러푸드2>\n\n검은색 식품은 보기와 달리 건강에 도움을 주는 경우가 많다. 강력한 항산화 물질인 '안토시아닌(Anthocyanin)' 성분이 많이 들었기 때문이다. 안토시아닌은 콜레스테롤 수치 저하, 혈관 보호, 항암, 궤양 예방 효능이 탁월하다고 알려졌다. 특히 흑미, 검정콩, 검정깨, 검정땅콩 등 검은색 '곡물'에 안토시아닌이 풍부하다. 농촌진흥청 국립식량과학원 기획조정과 곽도연 과장은 '면역력 강화가 중요성해진 요즘, 기능성 성분이 풍부한 검정 곡물을 섭취하면 건강 유지에 도움이 될 것'이라고 말했다.",
    "<달고 짠 음식 주의>\n\n푹푹 찌는 날씨에 식욕이 절로 꺾인다. 입맛을 돋우기 위해 달거나 짠 음식을 찾게 되는데, 이러한 식습관은 건강을 해칠 수 있어 조심해야 한다. 단짠단짠(달고 짠)’으로 통하는 자극적인 음식은 당뇨병, 고혈압 등 만성질환을 유발하는 주범이다.\n\n반복적으로 단 음식을 먹으면 혈당을 낮추는 인슐린에 대해 무뎌져 ‘저항성’이 생기고, 췌장 부담도 커져 인슐린 분비에 어려움이 생겨 당뇨병을 유발한다. 짠 음식을 먹으면 혈중 나트륨 농도가 증가해 혈관내 수분량이 증가한다. 이때 혈압이 점점 증가하면서 고혈압이 된다. 또 나트륨은 혈관을 딱딱하게 만들어 동맥경화증을 일으키고, 피떡(혈전)을 잘 생기게 만든다",
    "<탄산음료 과다섭취 주의>\n\n청량함이 반가운 무더운 계절이다. 하지만 '청량음료'라 불리는 '탄산음료'는 주의하는 게 좋다.\n탄산음료는 보통 정제당과 함께 정제수, 탄산가스, 구연산, 카페인, 인산, 그리고 색을 내는 합성착색제(캐러멜색소 등)나 향을 내는 합성착향료 등의 인공첨가물로 구성돼 있다. 특히 정제된 당이 많이 함유돼 문제다. 식품의약품안전처에 따르면 콜라 1캔(250㎖)에는 각설탕 7개에 달하는 평균 27ｇ의 당이 들어있다. 이는 WHO가 하루 당 섭취량으로 제한한 50ｇ의 절반을 넘는 수치다. 당분이 지방으로 축적되면 비만, 당뇨병, 동맥경화 등을 유발한다. 인산 성분은 세균과 곰팡이를 방지하고 톡 쏘는 맛을 전달하지만, 다량 또는 지속적으로 섭취할 경우 건강을 위협한다. 골다공증의 원인으로 지목당할 정도로 체내 칼슘을 배출 시켜 뼈를 약하게 하고, 오래 꾸준히 탄산음료를 마시면 치아가 부식되기 쉽다",
    "<항생제와 유산균 같이 먹으면 안돼>\n\n항생제는 몸에 침입한 균을 죽이는 역할을 한다. 그런데 유산균도 균의 일종이기 때문에 항생제와 함께 먹으면 유산균을 죽여 효과를 떨어트릴 수 있다. 유산균도 항생제의 약효를 감소시킨다. 따라서 유산균은 항생제 치료가 다 끝난 뒤에 먹는 게 좋다. 함께 먹고 싶다면 항생제 복용 2시간 후에 먹어야 한다. ",
    "<눈 건강에 중요한 비타민 A>\n\n안구건조증 및 야맹증을 겪고 있다면 비타민A를 섭취해야 한다. 비타민A는 눈의 점막을 보호하고 면역력을 유지시키며 시력을 지키는 데 가장 중요한 역할을 한다. 비타민A는 돼지나 소의 간, 달걀에 함유되어 있고, 채소나 과일 중에는 고구마, 시금치, 당근, 케일, 사과, 살구, 망고에 많다. 비타민C는 항산화 성분으로, 노안, 백내장 예방에 도움을 준다. 초봄이 제철인 봄동은 일반 배추보다 비타민C가 약 4배로 많고, 면역력 향상에도 도움을 줘 눈의 노화를 늦춘다고 알려졌다. 이밖에 브로콜리, 양파, 시큼한 레몬, 키위에도 많다. 비타민C는 많이 섭취해도 몸에서 필요한 만큼 쓰이고 배출되기 때문에 충분히 섭취하는 것이 좋다.",
    "<채소 껍질까지 먹으면..>\n\n채소나 과일 껍질에는 생각보다 영양소가 가득하고, 잘 조리하면 부담 없이 먹을 수 있다. 껍질에 남아 있는 잔류 농약이 걱정된다면 꼼꼼한 세척만으로도 남아있는 대부분의 농약을 제거할 수 있다. 1분 동안 물에 담가 놓은 후, 물을 버리고 새로운 물을 담아 저어주면서 30초 동안 세척하고, 마지막에는 흐르는 물로 헹구면 된다.\n양파에는 항산화 물질인 '폴리페놀'과 '퀘르세틴'이 가득한데, 양파 껍질에는 양파 속보다 폴리페놀이 20~30배, 퀘르세틴은 4배나 들어 있다. 육수를 끓일 때 양파를 껍질째로 넣으면 영양소를 더욱 가득 우려낼 수 있다. 날것으로 먹을 때보다 껍질의 식감도 좋아진다. ",
    "<비타민 E 결핍증>\n\n비타민E 결핍증에 대한 관심이 높아지면서 비타민E가 풍부한 음식에 대한 관심도 덩달아 높아지고 있다. 비타민E는 지용성 비타민의 한 가지로 우리 몸의 세포 노화를 막아주는 항산화 기능을 하는 영양소다. 또한 생식 기능과 근기능을 유지하는데 영향을 준다. 비타민 E가 부족하면 생식 기능이 저하되거나 빈혈이 일어날 수 있다. 또 근육이 제대로 기능을 하지 못해 근육이 위축되는 증상을 일으킬 수도 있다. 견과류, 시금치, 올리브유 등이 대표 음식이다. ",
    "<면역력 높이는 생활습관>\n\n 1. 현미처럼 도정이 덜 된 거친 곡류와 잡곡으로 밥 짓기\n ▶ 미네랄, 필수아미노산, 섬유질 등 영양성분이 풍부\n\n 2. 생선, 고기, 콩류 등 다양한 종류의 단백질군 섭취하기\n ▶ 단백질 식품 종류마다 함유하고 있는 미량영양소의 종류와 양이 다르기 때문\n\n 3. 다양한 색의 채소와 과일을 골고루 섭취하기\n\n ▶ 식물에 함유된 비타민과 파이토케미컬에 의해 색이 결정되기 때문\n (파이토케미컬: 건강에 도움을 주는 식물성 화학물질로 대표적으로 안토시아닌, 라이코펜, 카로티노이드 등이 있음)\n\n 4. 채소는 신선한 상태나 약간 데친 상태로 섭취하기\n ▶ 너무 많이 익히게 될 경우 채소 속 비타민이 파괴됨\n\n 5. 간식이 먹고 싶다면, 과자보단 견과류·발효유 섭취하기\n ▶ 프리바이오틱스가 풍부해 장내미생물을 건강하게 키워주기 때문\n\n 6. 탄산음료보단 섬유질이 살아있는 생과일 주스 섭취하기\n ▶ 단, 설탕 시럽은 적게 넣어 만들기 ",
    "<한국인에게 부족한 영양소 리보플라빈>\n\n 리보플라빈 급원식품으로 알려진 음식은 육류, 달걀, 생선, 우유다. 연구에 따르면 육류는 리보플라빈이 크게 풍부하지 않았다. 연구팀이 밝힌 식품별 1회 섭취량당 리보플라빈 함량은 닭고기의 경우 0.15㎎ 미만으로 아이스크림과 비슷한 수준이었으며, 소고기 역시 0.2~0.5㎎로 고사리보다 적었다. 연구에 따르면 고사리, 우유, 바지락조개, 고등어 등이 리보플라빈 급원식품이다. 리보플라빈이 부족하면 입술·눈꺼풀에 염증이 생길 수 있으며, 안구건조증도 찾아올 수 있다.",
    "<심장에 나쁜 음식>\n\n 심장에 나쁜 음식=튀김, 도넛, 밀가루, 가공육 등\n\n 심장 건강에 가장 안 좋은 음식은 트랜스 지방이다. 트랜스 지방은 체내 염증 물질을 증가시켜 혈관의 기능을 망가뜨리는데, 심장 세포에도 직접적인 영향을 끼쳐 협심증 등을 유발할 수 있다. 그 다음으로 안 좋은 음식은 가공육이다. 가공육은 살코기가 아닌 지방 부위를 많이 이용하기 때문에 콜레스테롤 함량이 높고, 보존을 위해 나트륨도 많이 넣어서 심장 혈관에 좋지 않다.\n\n 따라서 튀김이나 도넛 등 트랜스 지방이 든 음식은 가급적 먹지 말고, 가공육은 1주일에 먹는 양이 총 50g을 넘기지 말아야 한다. 정제된 곡물도 심장 건강에 안 좋다. 밀가루가 대표적인데, 이를 이용해 만든 빵·시리얼·면 같은 음식은 하루에 두 번 이하로 먹어야 한다. 한 번 먹을 때의 적정량은 빵 한 조각이나 시리얼 2분의 1컵 정도다. 가공하지 않은 붉은 고기는 정제된 곡물 다음으로 좋지 않은 만큼, 과도하게 먹지 않아야 한다.",
    "<더위에 시원한 맥주 주의>\n\n 날씨가 더운 여름에는 땀을 많이 흘려 체내 수분이 부족해진다. 이러한 상태에서 알코올의 이뇨작용까지 더해지면 미네랄 등과 함께 몸속 수분이 다량 배출돼 탈수 현상이 더 심해진다. 심각할 경우 탈수증으로 이어져 현기증, 구토 등의 증상이 나타나거나 탈진할 수도 있어 주의해야 한다.\n\n  또한 여름철 음주로 체내 수분이 부족해지면 혈중 알코올 농도가 급격히 상승해 취기가 빨리 오르고 혈액이 끈끈해져 동맥경화나 급성 심근경색과 같은 심혈관질환의 위험이 높아질 수 있다.\n\n  전용준 원장은 “기온이 높은 여름에는 체온을 조절하기 위해 혈관이 확장돼 알코올의 체내 흡수가 빨라져 다른 계절보다 취기가 빠르게 오른다”며 “특히 더위에 취약한 고혈압이나 당뇨병 환자의 경우 무더위에 술을 마시면 혈압과 혈당 조절에 문제가 생겨 증상이 악화되거나 심장마비와 같은 위험 상황이 발생할 수 있으므로 더욱 조심해야 한다”고 말했다.\n\n  음주로 인한 탈수증을 막기 위해선 음주 전후 물을 충분히 마셔 몸속 수분을 보충해 주는 것이 좋다. 무엇보다 여름철 음주가 건강에 악영향을 미칠 수 있는 만큼 술보다는 참외, 수박과 같은 수분 함량이 높은 과일을 먹거나 물을 마시는 등 건강한 수분 섭취 방법으로 더위와 갈증을 해소하는 것이 바람직하다.",
    "<물 건강하게 마시는 법>\n\n 물은 많이 먹어야 할 때가 있고, 적게 마셔야 할 때도 있다. 올바른 물 섭취 방법을 알아보자.\n\n  ◇설사한다면\n 설사를 하면 수분을 잃게 되므로 충분한 수분과 전해질 섭취가 중요하다. 물을 마실 수 있다면 충분히 마시는 게 좋다. 다만 복통·구토가 심해 물조차 마시기 어려우면 한 번에 억지로 많이 마시지 않는다. 입만 축일 정도로 조금씩 자주 마시면 된다.\n\n  ◇다이어트 중이라면\n 충분한 수분 공급은 신진대사를 원활히 한다. 물은 칼로리가 없으므로 많이 마셔도 살이 찌지 않는다. 다이어트로 인한 변비·탈수 예방도 가능하다.\n\n  ◇운동할 때\n 운동하기 30분쯤 전에 물을 한 잔 마신다. 운동 중에는 목이 마르지 않더라도 매시간 120∼240㏄의 물을 지속적으로 마신다. 갈증을 느낀다는 건 이미 몸속에 수분이 부족하다는 의미다. 수분이 부족하면 운동능력과 집중력이 떨어진다. 땀을 많이 흘리면 나트륨이 빠져나가기 때문에, 운동 후 스포츠음료로 미네랄을 함께 보충하면 좋다.\n\n  ◇식사 도중\n 물을 마시는 것이 신체에 큰 영향을 미치지는 않는다. 단, 식사 중간에 물을 많이 마시고 소화가 안 되는 경험을 했다면 줄이는 게 좋다.\n\n  ◇신장 안 좋으면\n 신장이 나빠지면 염분 처리를 못해 염분 과부하가 된다. 체내의 과도한 염분을 희석하려고 수분을 배출하지 않아 몸이 붓는다. 만성신부전 환자는 염분 섭취를 엄격히 제한한다. 만성신부전증처럼 특별한 경우를 제외하고 수분 섭취를 제한하지 않으나, 수분 배출량에 따라 섭취량을 결정한다.\n\n  ◇당뇨병이 있다면\n 소변과 땀의 배설량에 따라 수분을 보충하는 것이 일반적이다. 당뇨병 합병증으로 신장이 나빠지는 당뇨병성신병증이 있으면 과다한 수분 섭취가 부종을 가져올 수 있으므로 주의한다.",
    "<여름에 고기 꼭 익혀 드세요>\n\n 병원성 대장균 감염을 막으려면 주요 감염원인 육류는 속까지 충분히 익혀 먹어야 한다. 육류의 중심 온도(식품 중심부분 온도)는 75도 이상으로, 이 온도에서 1분 이상 가열해 먹어야 한다. 세브란스병원 영양팀 이송미 팀장은 '센 불에서 고기를 굽기보다 중간 불에 충분히 가열해 속까지 익혀야 한다'며 '햄버거 패티 등 가공 육류는 설익은 것을 먹으면 안 된다'고 말했다.\n\n  채소 역시 꼼꼼하게 흐르는 물에 3번 이상 씻어서 먹고, 이 때 전용 세정제를 이용하면 도움이 된다.  식중독 위험이 높은 한여름에는 생채소보다는 익혀서 먹을 것을 추천한다. 가정에서도 채소용·육류용·어류용 도마로 구분해서 사용하자. 가열 조리된 식품도 남았다면 빠른 시간 내 냉장 보관을 해야 한다.\n\n ",
    "<철분 결핍 막기 위해 적정 량의 육류 섭취해야>\n\n 철분은 크게 헴(heme)철과 비헴(non-heme)철 2가지 형태가 있다. 헴철은 육류·가금류·어류 등 동물성에 존재하고 비헴철은 곡류·콩류·채소류 등 식물성에 있다. 두 성분의 차이는 '체내 흡수량'이다. 동물성인 헴철은 체내에 15% 정도, 비헴철은 5% 정도만 흡수되므로 철분 결핍이 있다면 흡수가 잘 되는 헴철 음식 섭취가 권장된다.\n\n  철분은 대부분 신체에서 재활용되고, 소량만 손실된다(매일 남자 0.7㎎, 여자 1.2㎎). 이 양은 대부분 식사에서 대체할 수 있으므로 신경 써서 먹어야 한다. 김양현 교수는 '식물성 식품만 고집하면 흡수량이 적어 철분 결핍이 나타날 수 있다'며 '흡수가 잘 되는 동물성 식품(헴철)과 잘 안 되는 식물성 식품(비헴철)을 균형 있게 먹어 흡수율을 높이는 게 중요하다'고 말했다.\n\n  철분은 소실량만큼 먹으면 된다. 예를 들어 돼지고기 200g에는 12.8㎎의 철분이 들어있다. 여기서 10~15%가 들어오므로, 1.28~1.92㎎이 흡수된다. 성인 기준으로 남성과 여성 모두 소실량을 채울 수 있다. ",
    "<조기 사망 위험 높이는 가공식품 섭취량 줄여야>\n\n 가공식품 섭취가 크게 늘고 있다. 한국인은 얼마나 많은 가공식품을 섭취할까? 가공식품과 원재료식품의 섭취 비율이 7대3 정도로 가공식품 섭취가 많다.\n\n  가공식품을 완전히 먹지 않을 수는 없겠지만 가급적이면 가공이 덜 된 식품을 집에서 조리해서 먹는 것이 좋다. 가공식품을 먹을 때도 조금만 신경 쓰면 덜 해롭게 먹을 수 있다.\n\n  라면은 처음 면을 끓인 물은 버리고, 스프만 끓여 온도가 높은 물에 면을 넣고 끓여 먹는 것이 좋다. 용인대 식품영양학과 심선아 교수는 '이때도 스프를 절반만 넣는 것이 좋다'고 말했다. 어묵 역시 조리하기 전에 뜨거운 물에 살짝 데친 후 헹궈서 조리한다. 단무지는 조리 전 찬물에 5분 이상 담가 섭취하는 것이 좋다.\n\n  참치캔은 기름에도 식품첨가물이 있기 때문에 기름은 버리고 요리한다. 식빵은 팬이나 오븐에 살짝 구워 먹고, 두부는 먹기 전 찬물에 여러번 헹궈 요리하면 식품첨가물을 줄일 수 있다. 심선아 교수는 '식품첨가물 흡수를 줄이려면 채소 등 식이섬유를 충분히 같이 먹어라'라고 말했다.",
    "<컬러푸드:노란색>\n\n 노란색 식품은 호박, 고구마, 살구, 밤, 오렌지, 귤, 파인애플, 당근, 감, 옥수수 등이 있다. 노란색 식품은 항산화 작용을 하고, 노화를 예방하는 '카로티노이드'를 포함하고 있다. 카로티노이드는 심장질환과 암의 위험을 감소시키고, 면역기능을 향상시킬 수도 있다. 카로티노이드는 체내에서 비타민A로 전환된다. 비타민A는 시각과 면역기능뿐만 아니라 피부와 뼈 건강에도 중요하다. 노란색 식품에는 카로티노이드뿐 아니라 비타민 C, 오메가3 지방산, 엽산 등 풍부한 영양소가 포함돼 있다.",
    "<컬러푸드:초록색>\n\n 초록색 식품은 녹차, 매실, 브로콜리, 시금치, 매생이, 올리브유, 부추, 깻잎, 고춧잎, 알로에, 완두콩 등이 있다. 초록색을 띠게 만드는 엽록소는 신진대사를 원활하게 하고 피로를 풀어주며, 세포 재생을 도와준다. \n 초록색 채소들은 간 건강에 도움을 주는 '클로로필'이라는 파이토케미컬을 함유하고 있다. 초록색 채소 중 짙푸른 녹색 잎채소, 피스타치오, 콩류, 오이, 샐러리와 같은 식품에는 눈 건강에 중요한 루테인이 함유돼 있고, 브로콜리와 케일, 양배추에는 DNA 손상을 억제해 암을 예방하는 인돌 성분이 들어있다. 뽀빠이의 음식으로 불리는 시금치에는 엽산, 비타민 K, 칼륨, 카로티노이드가 풍부하다.",
    "<컬러푸드:보라색> \n\n 보라색 식품은 가지, 자두, 포도, 블루베리, 자색 고구마, 적채, 적양파 등이 있다. \n 보라색 식품에 함유된 파이토케미컬도 안토시아닌이다. 안토시아닌은 천연 항산화제로 세포 내 해로운 활성산소의 생성을 억제하고, 각종 질병으로부터 신체를 보호해주는 항바이러스 효과가 탁월해 노화를 막고 활력을 북돋는다. 눈의 피로 해소와 백내장 예방에도 도움이 된다. 보라색 식품에는 '폴리페놀' 성분도 풍부하다. 폴리페놀은 혈압, 염증, 콜레스테롤 수치를 낮추고 산화 스트레스를 줄여주는 식물성 화합물이다."]

morning_health_info_summary = ["항산화 작용과 암 예방 효능을 가진 컬러푸드 중 빨간색의 대표적 식품인 토마토",
                               "단백질 결핍을 방지하기 위해 매 끼니마다 적정한 양의 고기류 생선류 혹은 콩류 음식 섭취 권장",
                               "비타민 미네랄이 풍부한 채소, 과일 섭취를 통해 우울증 예방", "안토시아닌이 풍부한 콩 섭취 권장", "달고짠 음식 주의",
                               "뼈와 치아를 약하게 하는 탄산음료", "항생제와 유산균 같이 먹으면 안돼", "눈 건강을 위해 비타민 A가 풍부한 음식 섭취",
                               "항산화 물질 채소 껍질을 통해 섭취", "견과류 시금치 등 비타민 E가 풍부한 음식", "면역력 높이는 생활습관",
                               "유제품, 어류 등에 풍부한 리보플라빈 섭취를 통해 피부 기능 유지", "심장에 나쁜 음식, 트랜스 지방",
                               "더위에 시원한 맥주가 오히려 체내 수분을 감소시킬 수 있어", "물은 자신의 신체 상태에 맞게 적절히 섭취해야", "여름철에 고기를 익혀 먹는게 좋은 이유",
                               "철분 결핍 막기 위해 적정 량의 육류 섭취해야", "조기 사망 위험 높이는 가공식품 섭취량 줄여야",
                               "컬러푸드: 노화를 예방하는 영양소가 많이 든 노란색 과일과 채소", "컬러푸드: 암을 예방하는 성분이 많이 든 초록색",
                               "컬러푸드: 항바이러스, 항노화 성분이 많이 든 보라색"]

morning_ask_if_try = ["이거 실천 해볼꺼야?", "이거 해볼거야?", "이거 해 볼 수 있겠어?", "이거 해볼래?"]
morning_cheerup = ["오오~~ 그래 엄마 우리 해보자 !!!", "오!!! 짱이야 엄마!!", "나도 응원할게 !! 해보자!", "화이팅!!!", "화이팅>.<", "울 엄마 짱이네~",
                   "오~~ 좋다"]
morning_reject_why = ["이유가 뭐야??", "왜??", "이유가 뭔지 말해줄 수 있어?"]
morning_farewell = ["응 엄마 있다가 또 연락할게 ~", "있다 또 연락할게 받아줘~", "또 연락할게~", "또 봐~", "엄마 또 연락할게~", "있다 또 연락할게용", "또 연락할게용💕"]

# evening conversation info
evening_greeting = ["엄마 안녕? 끼니는 잘 챙겨 먹었어?", "엄마 오늘 식사는 잘 했지?", "엄마 바쁠텐데 밥은 잘 챙겨 먹었어?", "엄마 오늘은 뭐 좀 먹었어?",
                    "엄마 밥은 잘 챙겨먹고 있지?", "밥은 먹으면서 하는거지?", "엄마 밥 잘 먹고 있어?"]
evening_accomplishment = ["엄마 잘했어", "엄마 칭찬해!", "엄마 수고했어", "잘했어용~", "오~~ 잘했어", "굿굿~", "짱!"]
evening_nagging = ["식사는 꼭 해야지~~~엄마~~~", "엄마~ 왜 안먹었어 ㅠㅠ", "왜 그랬어 ㅠㅠ", "잉 왜 ㅠㅠ", "왜 ㅠㅠㅠㅠㅠ", "잘 먹어야해 엄마~", "밥 잘 챙겨먹어야지 ㅠㅠ"]
ask_meal = [" 뭐 먹었는지 물어봐두돼? 안먹었으면 안먹었다고 해줄 수 있어?", " 뭐먹었는데? 안먹었으면 안먹었다고 해줘", " 어떤거 먹었는데? 안먹었으면 안먹었다고 해줘"]
evening_ask_morning = ["아침" + x for x in ask_meal]
evening_ask_noon = ["점심" + x for x in ask_meal]
evening_ask_evening = ["저녁" + x for x in ask_meal]
evening_ask_photo = ["혹시 사진 찍어둔 거 있어?", "사진도 있어?", "사진있어??"]
evening_ask_send = ["보내줘~", "보내줭", "오! 보내줘~~"]
evening_ask_okay = "알겠어~"
evening_farewell = ["엄마 내가 많이 사랑해. 오늘 잠 푹자구 선풍기 끄고 자는거 잊지말구~~", "엄마 오늘도 수고했어. 보고싶당", "엄마 바빠도 밥은 꼭 챙겨먹어야해.. 잘자",
                    "엄마 굿나잇~~ 오늘도 좋은 꿈 꿔", "엄마 내일 또 연락할게 잘자구 싸랑해~", "엄마 항상 건강해야해. 그래야 나랑 여행 자주 가지~ 사랑해",
                    "엄마 오늘도 고생 많았어. 아무리 바빠도 밥 잘 챙겨먹고 건강하게!"]

# predefined keys
def encoded_keyboard(id, is_yn):
    if is_yn:
        return InlineKeyboardMarkup([[InlineKeyboardButton(
    "응", callback_data='yes'+id), InlineKeyboardButton("아니", callback_data='no'+id)]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton("응", callback_data='yes'+id)]])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("daily.log")
streamHandler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(streamHandler)


def log(message):
    logger.info(message)


def on_callback_query(msg):
    print(msg)


def get_meal_summary(update):
    print("started")
    try:
        message = update["message"]
        photos = message["photo"]
        return photos[len(photos) - 1]["file_id"]
    except:
        print("error loading meal summary")
        return ""


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = bot_url + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    url = bot_url + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def send_image(file_id, chat_id):
    url = bot_url + "sendPhoto?photo={}&chat_id={}".format(file_id, chat_id)
    print(url)
    get_url(url)


def send_info_image(idx, chat_id):
    url = bot_url + "sendPhoto?photo=https://donghoon.io/assets/images/chi2021-photo/{}.jpg&chat_id={}".format(
        str(idx + 1), chat_id)
    print(url)
    get_url(url)


def send_message_with_key(text, chat_id, key):
    bot.send_message(chat_id=chat_id, text=text, reply_markup=key)


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(datetime.now(timezone.utc).astimezone(
                pytz.timezone('Asia/Seoul')).hour, chat)
            print(text)
        except Exception as e:
            print(e)


def init_morning(id, idx):
    try:
        send_message_with_key(morning_greeting[idx % len(morning_greeting)], id, encoded_keyboard("morning", False))
        print("success")
    except Exception as e:
        print(e)


def init_evening(id, idx):
    try:
        send_message_with_key(evening_greeting[idx % len(evening_greeting)], id, encoded_keyboard("evening", True))
        print("success")
    except Exception as e:
        print(e)


def get_current_hour():
    return datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).hour


def get_current_minute():
    return datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).minute


def get_current_monthday():
    return str(datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).month) + str(
        datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).day)


def get_current_total_time():
    return str(datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).month) + str(
        datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Seoul')).isoformat())

def daily_json():
    return {"morning_init": False, "morning_resolution": False, "morning_resolution_done": False,
               "morning_reason_why": False, "evening_init": False, "evening_good": False, "evening_ask_morning": False,
               "evening_ask_morning_text": "", "evening_ask_morning_if_image": False,
               "evening_ask_morning_completed_image": False, "evening_ask_morning_image": False,
               "evening_ask_morning_image_url": "",
               "evening_ask_noon": False, "evening_ask_noon_text": "", "evening_ask_noon_if_image": False,
               "evening_ask_noon_completed_image": False, "evening_ask_noon_image": False,
               "evening_ask_noon_image_url": "", "evening_ask_evening": False, "evening_ask_evening_text": "",
               "evening_ask_evening_if_image": False, "evening_ask_evening_completed_image": False,
               "evening_ask_evening_image": False, "evening_ask_evening_image_url": "", "farewell_sent": False,
               "morning_agree": False,
               "morning_disagree_reason": "", "three_hour_past": False, "logged": False, "morning_response_time": "",
               "evening_response_time": ""}

def main():
    last_update_id = None

    current_loop_idx = 4

    elderly_init_complete = {
        "71": daily_json(),
        "72": daily_json(),
        "73": daily_json(),
        "74": daily_json(),
        "75": daily_json(),
        "76": daily_json(),
        "77": daily_json(),
        "78": daily_json(),
        "79": daily_json(),
        "710": daily_json(),
        "711": daily_json(),
        "712": daily_json(),
        "713": daily_json(),
        "714": daily_json(),
        "715": daily_json(),
        "716": daily_json(),
        "717": daily_json(),
        "718": daily_json(),
        "719": daily_json(),
        "720": daily_json(),
        "721": daily_json(),
        "722": daily_json(),
        "723": daily_json(),
        "724": daily_json(),
        "725": daily_json(),
        "726": daily_json(),
        "727": daily_json(),
        "728": daily_json(),
        "729": daily_json(),
        "730": daily_json(),
        "731": daily_json(),
        "81": daily_json(),
        "82": daily_json(),
        "83": daily_json(),
        "84": daily_json(),
        "85": daily_json(),
        "86": daily_json(),
        "87": daily_json(),
        "88": daily_json(),
        "89": daily_json(),
        "810": daily_json(),
        "811": daily_json(),
        "812": daily_json(),
        "813": daily_json(),
        "814": daily_json(),
        "815": daily_json()
    }

    while True:
        # handling initiating messages
        if get_current_hour() == elderly_preferred_time[0] and not elderly_init_complete[get_current_monthday()][
            "morning_init"]:
            init_morning(elderly_id, current_loop_idx)
            elderly_init_complete[get_current_monthday()]["morning_init"] = True
            current_loop_idx = current_loop_idx + 1  # increment index
        elif get_current_hour() == elderly_preferred_time[1] and not elderly_init_complete[get_current_monthday()][
            "evening_init"]:
            init_evening(elderly_id, current_loop_idx)
            elderly_init_complete[get_current_monthday()]["evening_init"] = True
        elif get_current_hour() == elderly_preferred_time[1] + 3 and not elderly_init_complete[get_current_monthday()][
            "evening_ask_evening"] and not elderly_init_complete[get_current_monthday()]["three_hour_past"]:
            if not elderly_init_complete[get_current_monthday()]["morning_reason_why"]:
                send_message_with_key("{}님이 오늘 영양관리 봇을 사용하지 않으셨네요 ㅜㅜ 지금 {}님께 직접 연락해보시겠어요?".format(
                    elderly_name, elderly_name), receiver_id, encoded_keyboard("sendmessage", True))
            else:
                if elderly_init_complete[get_current_monthday()]["morning_agree"]:
                    send_message("오늘 {}님은 {} 기사를 받아보셨습니다. 이를 실천 할 의지가 있다고 얘기하셨습니다.".format(
                        elderly_name, morning_health_info_summary[current_loop_idx % len(morning_health_info_summary)]),
                        receiver_id)
                else:
                    send_message("오늘 {}님은 {} 기사를 받아보셨습니다. 이를 실천 할 의지가 없다고 얘기하셨고 이유는 '{}' 라고 합니다.".format(
                        elderly_name, morning_health_info_summary[current_loop_idx % len(morning_health_info_summary)],
                        elderly_init_complete[get_current_monthday()]["morning_disagree_reason"]), receiver_id)
                send_message_with_key("그런데 {}님이 오늘 어떤 식사를 하셨는지 입력을 안해주셨네요 ㅠㅠ 지금 {}님께 직접 연락해보시겠어요?".format(
                    elderly_name, elderly_name), receiver_id, encoded_keyboard("sendmessage", True))
            elderly_init_complete[get_current_monthday()]["three_hour_past"] = True

        if get_current_hour() == 23 and get_current_minute() > 30 and not elderly_init_complete[get_current_monthday()][
            "logged"]:
            log(
                "{" + '"date": "{}", "id": "{}", "morning.ms.time": {}, "morning.rp": {}, "morning.rp.time": "{}", "health.information": "{}", "behavior": {}, "behavior.reason": "{}", "dinner.ms.time": {}, "dinner.rp": {}, "dinner.rp.time": "{}", "breakfast": "{}", "breakfast.image": {}, "breakfast.image.file": "{}", "lunch": "{}", "lunch.image": {}, "lunch.imagefile": "{}", "dinner": "{}", "dinner.image": "{}", "dinner.imagefile": "{}"'.format(
                    get_current_monthday(), elderly_name, elderly_preferred_time[0],
                    elderly_init_complete[get_current_monthday()]["morning_resolution"],
                    elderly_init_complete[get_current_monthday()]["morning_response_time"],
                    morning_health_info_summary[current_loop_idx % len(morning_health_info_summary)],
                    elderly_init_complete[get_current_monthday()]["morning_agree"],
                    elderly_init_complete[get_current_monthday()]["morning_disagree_reason"], elderly_preferred_time[1],
                    elderly_init_complete[get_current_monthday()]["evening_good"],
                    elderly_init_complete[get_current_monthday()]["evening_response_time"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image_url"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image_url"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image_url"]) + "}")
            
            try:
                sheet.append_row([get_current_monthday(), elderly_name, elderly_preferred_time[0],
                    elderly_init_complete[get_current_monthday()]["morning_resolution"],
                    elderly_init_complete[get_current_monthday()]["morning_response_time"],
                    morning_health_info_summary[current_loop_idx % len(morning_health_info_summary)],
                    elderly_init_complete[get_current_monthday()]["morning_agree"],
                    elderly_init_complete[get_current_monthday()]["morning_disagree_reason"], elderly_preferred_time[1],
                    elderly_init_complete[get_current_monthday()]["evening_good"],
                    elderly_init_complete[get_current_monthday()]["evening_response_time"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image_url"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image_url"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"],
                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image_url"]])
            except:
                print("error logging on a spreadsheet")
            
            elderly_init_complete[get_current_monthday()]["logged"] = True

        # handling user-sent messages
        updates = get_updates(last_update_id)

        try:
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
            for update in updates["result"]:
                print(update)
                try:
                    text = ""
                    markup = 0
                    try:
                        text = update["message"]["text"]
                    except:
                        print("message without text")
                    try:
                        text = update["callback_query"]["data"]
                        markup = len(update["callback_query"]["message"]["reply_markup"]["inline_keyboard"][0])
                        print(markup)
                        bot.answer_callback_query(
                            update["callback_query"]["id"])
                    except:
                        print("message without callback")

                    try:
                        if "photo" in update["message"]:
                            markup = 3
                    except:
                        print("error processing photo")

                    if get_current_hour() >= elderly_preferred_time[0] and get_current_hour() < elderly_preferred_time[1] - 1:
                        # handle morning talk here
                        print(elderly_init_complete[get_current_monthday()]["morning_resolution"])
                        if not elderly_init_complete[get_current_monthday()]["morning_resolution"] and (text == "응" or (text == "yesmorning" and markup == 1)):

                            elderly_init_complete[get_current_monthday()][
                                "morning_response_time"] = get_current_total_time()

                            try:
                                send_message(morning_health_info[current_loop_idx % len(morning_health_info)],
                                             elderly_id)
                                send_info_image(current_loop_idx % len(morning_health_info), elderly_id)
                                send_message_with_key(
                                    morning_ask_if_try[current_loop_idx % len(morning_ask_if_try)], elderly_id,
                                    encoded_keyboard("health", True))
                                elderly_init_complete[get_current_monthday(
                                )]["morning_resolution"] = True
                            except Exception as e:
                                print(e)
                        elif not elderly_init_complete[get_current_monthday()]["morning_resolution_done"]:
                            if text == "응" or (text == "yeshealth" and markup == 2):
                                try:
                                    elderly_init_complete[get_current_monthday(
                                    )]["morning_resolution_done"] = True
                                    elderly_init_complete[get_current_monthday(
                                    )]["morning_reason_why"] = True
                                    elderly_init_complete[get_current_monthday()]["morning_agree"] = True
                                    send_message(morning_cheerup[current_loop_idx % len(morning_cheerup)], elderly_id)
                                    send_message(morning_farewell[current_loop_idx % len(morning_farewell)], elderly_id)
                                except Exception as e:
                                    print(e)
                            elif text == "아니" or (text == "nohealth" and markup == 2):
                                try:
                                    elderly_init_complete[get_current_monthday()]["morning_resolution_done"] = True
                                    elderly_init_complete[get_current_monthday()]["morning_agree"] = False
                                    send_message(morning_reject_why[current_loop_idx % len(morning_reject_why)], elderly_id)
                                except Exception as e:
                                    print(e)
                        elif not elderly_init_complete[get_current_monthday()]["morning_reason_why"] and markup == 0:
                            try:
                                elderly_init_complete[get_current_monthday(
                                )]["morning_reason_why"] = True
                                send_message(morning_farewell[current_loop_idx % len(morning_farewell)], elderly_id)
                                if len(text) > 1:
                                    elderly_init_complete[get_current_monthday(
                                    )]["morning_disagree_reason"] = text
                                    print(
                                        elderly_init_complete[get_current_monthday()]["morning_disagree_reason"])
                            except Exception as e:
                                print(e)







                    # ask evening
                    elif get_current_hour() >= elderly_preferred_time[1] and get_current_hour() < 24:
                        # handle evening talk here
                        if not elderly_init_complete[get_current_monthday()]["evening_good"]:

                            elderly_init_complete[get_current_monthday()][
                                "evening_response_time"] = get_current_total_time()

                            if text == "yesevening" and markup == 2:
                                try:
                                    elderly_init_complete[get_current_monthday()]["evening_good"] = True
                                    send_message(evening_accomplishment[current_loop_idx % len(evening_accomplishment)],
                                                 elderly_id)
                                    send_message(evening_ask_morning[current_loop_idx % len(evening_ask_morning)],
                                                 elderly_id)
                                except Exception as e:
                                    print(e)
                            elif text == "noevening" and markup == 2:
                                try:
                                    elderly_init_complete[get_current_monthday()]["evening_good"] = True
                                    send_message(evening_nagging[current_loop_idx % len(evening_nagging)], elderly_id)
                                    send_message(evening_ask_morning[current_loop_idx % len(evening_ask_morning)],
                                                 elderly_id)
                                except Exception as e:
                                    print(e)
                            else:
                                continue



                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_morning"] and markup == 0:
                            try:
                                elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"] = text
                                elderly_init_complete[get_current_monthday()]["evening_ask_morning"] = True
                                send_message_with_key(evening_ask_photo[current_loop_idx % len(evening_ask_photo)], elderly_id, encoded_keyboard("ask_morning", True))
                            except Exception as e:
                                print(e)

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_morning_if_image"]:
                            if text == "yesask_morning" and markup == 2:
                                try:
                                    send_message(evening_ask_send[current_loop_idx % len(evening_ask_send)], elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_if_image"] = True
                                except Exception as e:
                                    print(e)
                            elif text == "noask_morning" and markup == 2:
                                try:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_if_image"] = True
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_morning_completed_image"] = True
                                    send_message(evening_ask_noon[current_loop_idx % len(evening_ask_noon)], elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"] = False
                                except Exception as e:
                                    print(e)
                            else:
                                continue

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_morning_completed_image"]:
                            try:
                                if "photo" in update["message"] and markup == 3:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"] = True
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_morning_completed_image"] = True
                                    send_message(evening_ask_noon[current_loop_idx % len(evening_ask_noon)], elderly_id)
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_morning_image_url"] = get_meal_summary(update)
                                else:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"] = False
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_morning_completed_image"] = True
                                    send_message(evening_ask_noon[current_loop_idx % len(evening_ask_noon)], elderly_id)
                            except Exception as e:
                                print(e)




                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_noon"] and markup == 0:
                            try:
                                elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"] = text
                                elderly_init_complete[get_current_monthday()]["evening_ask_noon"] = True
                                send_message_with_key(evening_ask_photo[current_loop_idx % len(evening_ask_photo)],
                                                      elderly_id, encoded_keyboard("ask_noon", True))
                            except Exception as e:
                                print(e)

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_noon_if_image"]:
                            if text == "yesask_noon" and markup == 2:
                                try:
                                    send_message(evening_ask_send[current_loop_idx % len(evening_ask_send)], elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_if_image"] = True
                                except Exception as e:
                                    print(e)
                            elif text == "noask_noon" and markup == 2:
                                try:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_if_image"] = True
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_noon_completed_image"] = True
                                    send_message(evening_ask_evening[current_loop_idx % len(evening_ask_evening)],
                                                 elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"] = False
                                except Exception as e:
                                    print(e)
                            else:
                                continue

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_noon_completed_image"]:
                            try:
                                if "photo" in update["message"] and markup == 3:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"] = True
                                    elderly_init_complete[get_current_monthday()][
                                        "evening_ask_noon_completed_image"] = True
                                    send_message(evening_ask_evening[current_loop_idx % len(evening_ask_evening)], elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image_url"] = get_meal_summary(update)
                                else:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"] = False
                                    elderly_init_complete[get_current_monthday()]["evening_ask_noon_completed_image"] = True
                                    send_message(evening_ask_evening[current_loop_idx % len(evening_ask_evening)], elderly_id)
                            except Exception as e:
                                print(e)




                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_evening"] and markup == 0:
                            try:
                                elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"] = text
                                elderly_init_complete[get_current_monthday()]["evening_ask_evening"] = True
                                send_message_with_key(evening_ask_photo[current_loop_idx % len(evening_ask_photo)], elderly_id, encoded_keyboard("ask_evening", True))
                            except Exception as e:
                                print(e)

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_evening_if_image"]:
                            if text == "yesask_evening" and markup == 2:
                                try:
                                    send_message(evening_ask_send[current_loop_idx % len(evening_ask_send)], elderly_id)
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_if_image"] = True
                                except Exception as e:
                                    print(e)
                            elif text == "noask_evening" and markup == 2:
                                try:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_if_image"] = True
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_completed_image"] = True
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"] = False
                                    send_farewell_and_report(elderly_init_complete, current_loop_idx, elderly_init_complete[get_current_monthday()]["morning_resolution_done"])
                                except Exception as e:
                                    print(e)
                            else:
                                continue

                        elif not elderly_init_complete[get_current_monthday()]["evening_ask_evening_completed_image"]:
                            try:
                                if "photo" in update["message"] and markup == 3:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"] = True
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_completed_image"] = True
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image_url"] = get_meal_summary(update)
                                else:
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"] = False
                                    elderly_init_complete[get_current_monthday()]["evening_ask_evening_completed_image"] = True
                                send_farewell_and_report(elderly_init_complete, current_loop_idx, elderly_init_complete[get_current_monthday()]["morning_resolution_done"])
                            except Exception as e:
                                print(e)


                except Exception as e:
                    print(e)
        except:
            print("error getting updates")

        # sleep
        time.sleep(0.5)


def send_farewell_and_report(elderly_init_complete, current_loop_idx, is_morning_complete):
    if is_morning_complete:
        try:
            send_message(evening_farewell[current_loop_idx % len(evening_farewell)], elderly_id)
            elderly_init_complete[get_current_monthday()]["farewell_sent"] = True
            send_message("오늘 {}님의 식사일지입니다.".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["morning_agree"]:
                send_message("오늘 {}님은 {} 기사를 받아보셨습니다. 이를 실천 할 의지가 있다고 얘기하셨습니다.".format(elderly_name,
                                                                                       morning_health_info_summary[
                                                                                           current_loop_idx % len(
                                                                                               morning_health_info_summary)]),
                             receiver_id)
            else:
                send_message("오늘 {}님은 {} 기사를 받아보셨습니다. 이를 실천 할 의지가 없다고 얘기하셨고 이유는 '{}' 라고 합니다.".format(elderly_name,
                                                                                                     morning_health_info_summary[
                                                                                                         current_loop_idx % len(
                                                                                                             morning_health_info_summary)],
                                                                                                     elderly_init_complete[
                                                                                                         get_current_monthday()][
                                                                                                         "morning_disagree_reason"]),
                             receiver_id)
            send_message("{}님의 아침식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"], receiver_id)
                bot.send_photo(receiver_id,
                               elderly_init_complete[get_current_monthday()]["evening_ask_morning_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"], receiver_id)
            send_message("{}님의 점심식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"], receiver_id)
                bot.send_photo(receiver_id, elderly_init_complete[get_current_monthday()]["evening_ask_noon_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"], receiver_id)
            send_message("{}님의 저녁식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"], receiver_id)
                bot.send_photo(receiver_id,
                               elderly_init_complete[get_current_monthday()]["evening_ask_evening_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"], receiver_id)
        except Exception as e:
            print(e)
    else:
        try:
            send_message(evening_farewell[current_loop_idx % len(evening_farewell)], elderly_id)
            elderly_init_complete[get_current_monthday()]["farewell_sent"] = True
            send_message("{}님은 오늘 건강정보는 받아보지 않으셨습니다.".format(elderly_name), receiver_id)
            send_message("오늘 {}님의 식사일지입니다.".format(elderly_name), receiver_id)
            send_message("{}님의 아침식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_morning_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"], receiver_id)
                bot.send_photo(receiver_id, elderly_init_complete[get_current_monthday()]["evening_ask_morning_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_morning_text"], receiver_id)
            send_message("{}님의 점심식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_noon_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"], receiver_id)
                bot.send_photo(receiver_id, elderly_init_complete[get_current_monthday()]["evening_ask_noon_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_noon_text"], receiver_id)
            send_message("{}님의 저녁식사".format(elderly_name), receiver_id)
            if elderly_init_complete[get_current_monthday()]["evening_ask_evening_image"]:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"], receiver_id)
                bot.send_photo(receiver_id, elderly_init_complete[get_current_monthday()]["evening_ask_evening_image_url"])
            else:
                send_message(elderly_init_complete[get_current_monthday()]["evening_ask_evening_text"], receiver_id)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()