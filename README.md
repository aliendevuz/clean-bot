# Clean Bot Sample

Eng toza usulda bot yasash ustida tadqiqot o'tkazish

# Project Structure

```python
core/ # bu yerda bot yasash uchun base funksiyalarni yozib olaman
  base_repository.py
  nav_stack_manager.py
  state_manager.py
src/
  config/
    env.py # dotenvdan ma'lumot olish
  data/
    sqlite/
      user_db.py # turli db lar o'tasida oson transformatiya uchun
    postgres/
      user_db.py # bu esa postgresga moslab yozilgani
    repository/
      user_repo_impl.py # interfacedan implement qilishi va data bilan bog'lash
      *_repo_impl.py # boshqa implementlar
  core/ # domainga o'xshash qism
    models/ # barcha umumiy modellar
      user.py # misol sifatida user repo ni oldik
      *.py # qolgan modellar
    repositories/ # repository interfacelari
      user_repo.py # base_repository asosida repository interface (qaytaraman bu haqiqiy MVVM emas, shuning uchun core qismiga bog'lanishini normal)
      *_repo.py # boshqa repo interfacelar
    services/ # usecasega o'xshab amal bajaradigan qismi
      user_service.py # usecasedan farqli o'laroq barcha usecaselarni bitta faylda jamlaydi
      *_setvice.py # boshqa servicelar
  presentation/
    handlers/ # handler barcha eventlarni qabul qilish uchun
      commands/ 
        start.py
      callbacks/
        set_language.py
      messages/
        *.py # keyboard buttondan kelgan yoki oddiy matnlar uchun
    renders/ # render esa userga javob berishda chiqaradigan UI ga javob beradi
      keyborad/ # keyboardni renderaydi
        inline/ # inline uchun
        reply/ # reply keyboard uchun
      page/
        home.py # page bu navigation stack bo'yicha user hozir qayerda turganini aytadigan qismi
        settings.py # sahifaga xos matnlarni i18n dan olib renderlovchi
        *.py # boshqa sahifalar
      i18n/
        en.py # tarjima matnlari uchun
        uz.py # tarjima matnlari uchun
        ru.py # tarjima matnlari uchun
        i18n.py # mana shu instance tarjimalarni olib beradi
  app.py # barcha narsa mana shu yerda ulanadi
main.py # entry point
```

# User flow

```yml
bot:
  entry:
    command: /start
    flow:
      - check_user_exists
      - if_new_user:
          go_to: language_selection
      - if_existing_user:
          go_to: home_page

  language_selection:
    type: page
    ui:
      message: choose_language
      inline_buttons:
        - uz
        - en
        - ru
    on_select:
      - save_language
      - go_to: home_page

  home_page:
    type: page
    ui:
      message: main_menu
      inline_buttons:
        - addition
        - subtraction
        - multiplication
        - division
        - settings

  settings:
    type: page
    ui:
      message: settings_menu
      inline_buttons:
        - change_name
        - change_language
        - back
    flows:
      change_name:
        - ask_name
        - save_name
        - go_to: settings
      change_language:
        - go_to: language_selection
      back:
        - go_to: home_page

  operation_selection:
    triggered_by:
      - addition
      - subtraction
      - multiplication
      - division
    flow:
      - set_operation_type
      - go_to: level_list

  level_list:
    type: page
    ui:
      message: choose_level
      inline_buttons:
        levels: 1..10
        back: home_page

  level:
    type: stateful_page
    on_enter:
      - set_level
      - generate_question_pool
    flow:
      - go_to: question

  question:
    type: state
    logic:
      - generate_math_question:
          based_on:
            operation_type
            level
    delivery:
      if_quiz_supported:
        send: telegram_quiz
      else:
        send:
          message: question_text
          inline_buttons: answer_options

  answer_processing:
    on_answer:
      - validate_answer
      - save_result
      - if_correct:
          go_to: next_question_or_finish
      - if_wrong:
          go_to: retry_or_next

  next_question_or_finish:
    condition:
      if_questions_left:
        go_to: question
      else:
        go_to: level_result

  level_result:
    type: page
    ui:
      message: level_summary
      inline_buttons:
        - retry_level
        - choose_another_level
        - back_to_home

  retry_level:
    flow:
      - reset_level_state
      - go_to: question

  choose_another_level:
    flow:
      - go_to: level_list

  back_to_home:
    flow:
      - clear_navigation_stack
      - go_to: home_page

```

# 📘 Math Train Bot — App Specification (Bussines Logic)
1. App Purpose

Math Train Bot — bu foydalanuvchining arifmetik ko‘nikmalarini bosqichma-bosqich (level-based) rivojlantiruvchi Telegram bot.

Bot:

foydalanuvchini mashq jarayonida olib boradi

murakkablikni asta oshiradi

har bir amalni alohida trening sifatida tashkil qiladi

2. Core Concepts
2.1 User

Har bir user quyidagi minimal ma’lumotlarga ega:

id

name

language

created_at

User botni birinchi marta ishga tushirganda majburiy til tanlaydi.

2.2 Operation Types

Bot quyidagi matematik operatsiyalarni qo‘llab-quvvatlaydi:

addition

subtraction

multiplication

division

Har bir operation:

alohida trening sifatida ishlaydi

level progression bir-biridan mustaqil

2.3 Levels

Har bir operation 1 dan 10 gacha levelga ega.

Level — bu:

savollar murakkabligini

sonlar diapazonini

savollar sonini

belgilovchi biznes qoidalar to‘plami.

3. Level Difficulty Rules

Level murakkabligi oldindan belgilangan qoidalar asosida hisoblanadi.

Misol (konseptual):

Level 1:

1 xonali sonlar

5 ta savol

Level 2:

1 xonali, lekin sonlar oralig‘i kengroq

5–10 ta savol

Level 3:

2 xonali sonlar

Level 4–6:

murakkabroq kombinatsiyalar

Level 7–10:

yuqori murakkablik (katta sonlar, kamroq vaqt, kamroq variant)

AI levelni matematik formula emas, balki biznes qoida sifatida qabul qilishi kerak.

4. Question Generation Rules

Har bir savol:

tanlangan operation

joriy level

asosida dinamik tarzda generatsiya qilinadi.

Savol quyidagilarga ega bo‘lishi kerak:

savol matni

1 ta to‘g‘ri javob

2–3 ta noto‘g‘ri variant

Noto‘g‘ri variantlar:

mantiqan yaqin

tasodifiy, lekin real ko‘rinadigan bo‘lishi kerak

5. Question Delivery Rules

Bot savol yuborishda quyidagi ustuvorlikka amal qiladi:

Agar Telegram Quiz (poll) mavjud bo‘lsa:

quiz formatida yuboriladi

Aks holda:

oddiy message

inline button orqali javob variantlari

Bu tanlov presentation layer mas’uliyati hisoblanadi,
biznes mantiqqa ta’sir qilmaydi.

6. Answer Processing Rules

Foydalanuvchi javob berganda:

javob tekshiriladi

natija saqlanadi

to‘g‘ri yoki noto‘g‘ri ekanligi aniqlanadi

Bot:

noto‘g‘ri javobda foydalanuvchini to‘xtatmaydi

trening davom etadi

7. Progress & Completion Rules

Level:

oldindan belgilangan savollar soni tugaganda yakunlanadi

Level yakunida:

qisqa natija ko‘rsatiladi

foydalanuvchi quyidagilardan birini tanlaydi:

shu levelni qayta bajarish

boshqa level tanlash

bosh sahifaga qaytish

8. Navigation Rules

Bot:

sahifalar orasida harakatni navigation stack orqali boshqaradi

foydalanuvchi har doim:

ortga qaytishi

treningni qayta boshlashi

boshqa yo‘lni tanlashi mumkin

State:

operation

level

question index

doimiy nazorat ostida bo‘lishi kerak.

9. Separation of Responsibilities

Handlers

faqat event qabul qiladi

Services

barcha biznes qoidalarni bajaradi

Repositories

user va progress ma’lumotlarini saqlaydi

Renders

foydalanuvchiga ko‘rinadigan UI ni generatsiya qiladi

# 