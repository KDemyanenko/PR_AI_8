"""Створює фінальний PDF українською, без нумерації та кольорового декору."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
import json

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

R=Path(__file__).resolve().parents[1]
OUT=R/'docs/PR8_Final_Report.pdf'
TEMP=R/'docs/_report_text.pdf'
ARCH=R/'docs/_architecture_page.pdf'
metrics=json.loads((R/'results/metrics.json').read_text(encoding='utf-8'))

pdfmetrics.registerFont(TTFont('Tinos', '/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Tinos-Bold', '/usr/share/fonts/truetype/croscore/Tinos-Bold.ttf'))
pdfmetrics.registerFontFamily('Tinos',normal='Tinos',bold='Tinos-Bold')

BODY=ParagraphStyle('body',fontName='Tinos',fontSize=14,leading=17.5,spaceAfter=6,textColor=colors.black)
HEAD=ParagraphStyle('head',parent=BODY,fontName='Tinos-Bold',fontSize=15.5,leading=20,spaceBefore=10,spaceAfter=5,keepWithNext=True)
TITLE=ParagraphStyle('title',parent=BODY,fontName='Tinos-Bold',fontSize=18,leading=24,alignment=TA_CENTER,spaceAfter=12)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=12.2,leading=15,spaceAfter=1)
CELL=ParagraphStyle('cell',parent=BODY,fontSize=12.2,leading=14.8,spaceAfter=0)
TH=ParagraphStyle('th',parent=CELL,fontName='Tinos-Bold')
NOTE=ParagraphStyle('note',parent=BODY,fontSize=12,leading=16)

def p(s,style=BODY):return Paragraph(s,style)
def text(s,style=BODY):return p(escape(str(s)),style)
def grid(rows,widths,headers=True):
    content=[]
    for i,row in enumerate(rows):
        content.append([p(str(item), TH if (headers and i==0) else CELL) for item in row])
    t=Table(content,colWidths=widths,repeatRows=1 if headers else 0,hAlign='LEFT',splitByRow=1)
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),
          ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
          ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
          ('LINEBELOW',(0,0),(-1,0),0.65,colors.black),
          ('LINEBELOW',(0,1),(-1,-1),0.25,colors.black),
          ('LINEBEFORE',(0,0),(0,-1),0.3,colors.black),
          ('LINEAFTER',(-1,0),(-1,-1),0.3,colors.black)]
    if headers:cmds.append(('LINEABOVE',(0,0),(-1,0),0.65,colors.black))
    t.setStyle(TableStyle(cmds))
    return t

story=[]
story += [text("Дем'яненко Микола 242 2 практична 8"),
          p('Фінальний проєкт системи керування поведінкою NPC із компонентом штучного інтелекту',TITLE)]
story += [p('1. Проблема, система і межі реалізації',HEAD),
          p('<b>Проблема.</b> NPC із фіксованими правилами можуть неправильно реагувати на загрозу й бути занадто передбачуваними.'),
          p('<b>Рішення.</b> Спроєктовано систему з восьми компонентів для отримання ігрового стану, аналізу ситуації, оцінювання загрози, вибору дозволеної дії та її передавання рушію.'),
          p('<b>Користувачі.</b> Гравець бачить поведінку NPC; розробник налаштовує правила; QA перевіряє помилки. Ігровий рушій передає події й виконує команди.'),
          p('<b>Реально реалізовано.</b> Python-прототип моделі оцінювання загрози (C4) і перевірки рекомендації (C5/C7, DP-07). Повна гра, навігація NavMesh та виконання дій у рушії поки не реалізовані.'),
          p('2. Основні компоненти логічної архітектури',HEAD)]
component_rows=[
 ['Код','Функція компонента','Обмін даними'],
 ['C1','Інтеграція з рушієм','Приймає події; надсилає перевірені команди'],
 ['C2','Менеджер стану NPC','Оновлює HP, координати й стан; D2'],
 ['C3','Сприйняття світу','Створює ознаки: дистанція, видимість, укриття'],
 ['C4','Компонент ШІ (ML)','Отримує ознаки; повертає score і confidence; D3'],
 ['C5','Планувальник поведінки','Обирає дію DP-07 та ціль DP-08'],
 ['C6','Навігація','Перевіряє маршрути DP-08/DP-09'],
 ['C7','Правила й обмеження','Перевіряє дозвіл і безпечність дій; D1'],
 ['C8','Налаштування та моніторинг','Правила розробника, журнал і перегляд QA; D4'],
]
story += [grid(component_rows,[35*mm,53*mm,92*mm]),
          Spacer(1,7),
          p('Сховища даних: <b>D1</b> — правила й пороги; <b>D2</b> — стани NPC; <b>D3</b> — модель; <b>D4</b> — журнал рішень. Повна діаграма наведена далі.',NOTE),
          PageBreak()]

story += [p('3. Узгодженість із ПР-1–ПР-7',HEAD),
          grid([
           ['Робота','Що збережено у фінальній версії'],
           ['ПР-1','Межі NPC-системи; гравець, рушій, ігровий світ'],
           ['ПР-2','Здоров’я, координати, відстань, видимість, оточення'],
           ['ПР-3','UC-01–UC-08; DP-01–DP-14; HITL та запасні правила'],
           ['ПР-4','Компоненти C1–C8, сховища D1–D4 та напрями передачі даних'],
           ['ПР-5','Оцінка загрози як задача ML + Rule-based; DP-07'],
           ['ПР-6','Працюючий Notebook; дані 400, навчання 300, тест 100'],
           ['ПР-7','16 тестів, три проблеми ML, нові правила confidence 0,80/0,65'],
          ],[31*mm,149*mm]),
          p('4. Повний сценарій UC-04 «Відступити у разі небезпеки»',HEAD)]
steps=[
 '1. <b>Гравець</b> атакує NPC; <b>C1</b> отримує від рушія подію пошкодження.',
 '2. <b>C2</b> оновлює HP і координати, а <b>C3</b> обчислює відстань та ознаки оточення.',
 '3. <b>C4</b> (ML) формує <i>threat_score</i> та <i>confidence</i>.',
 '4. <b>C5 + C7, DP-07:</b> якщо втеча дозволена і (HP ≤ 25% або threat_score ≥ 0,85), обирається відступ. Правила C7 можуть заборонити втечу босу.',
 '5. <b>C5 + C6, DP-08:</b> обирається досяжна точка відступу; <b>C6 + C7, DP-09</b> перевіряють шлях.',
 '6. Після дозволу C7 команда повертається через <b>C1</b> до рушія, а <b>C8/D4</b> зберігають причину рішення для QA.',
]
story.extend([p(s) for s in steps]); story.append(p('<b>Межа прототипу:</b> у Python відтворено аналіз ознак і результат DP-07; пункти 1, 5, 6 — архітектурний план, а не підключена гра.',NOTE))

story.extend([p('5. Прототип і фактичні результати',HEAD),
   p('Застосовано <b>RandomForestClassifier</b> (100 дерев, seed=42) на 400 синтетичних записах, із яких 300 — навчальні, 100 — відкладені тестові. Ознаки: HP, дистанція, сила ворога, видимість, укриття. Еталонну мітку створює формула; це не реальні ігрові логи.'),
   grid([
     ['Показник','Фактичний результат'],
     ['Точність класифікації',f"(63 TN + 28 TP) / 100 = <b>{str(round(metrics['accuracy']*100,1)).replace('.',',')}%</b>"],
     ['Повнота високої загрози',f"28 TP / (28 TP + 8 FN) = <b>{str(round(metrics['recall_high_threat']*100,1)).replace('.',',')}%</b>"],
     ['Матриця помилок','TN=63; FP=1; FN=8; TP=28'],
     ['Контрольні ситуації',f"<b>{metrics['controlled_correct']} / {metrics['controlled_cases']}</b> рекомендованих дій збіглися з очікуваними"],
     ['Автоматизовані тести','<b>6 із 6</b> пройдені (модель, правила, QA, відмова)'],
   ],[81*mm,99*mm]),
   p('16/16 означає відповідність заздалегідь визначеним тестовим сценаріям, <b>а не</b> 100% якість у грі. Значення confidence не калібровані.',NOTE)
])

story.extend([p('6. Як використовуються оцінки ШІ',HEAD),
 grid([
  ['Умова','Результат'],
  ['confidence ≥ 0,80','Автоматично застосувати ML за коректних даних і перевірки C7'],
  ['0,65 ≤ confidence < 0,80','Резервне правило HP; записати на післяігровий огляд QA'],
  ['confidence < 0,65 або модель недоступна','Відхилити ML; fallback за HP, якщо дані достовірні'],
  ['Відсутні/некоректні критичні дані','Не починати нову неперевірену дію; безпечна зупинка'],
  ['Втечу заборонено правилами','C7 блокує відступ незалежно від рекомендації'],
 ],[72*mm,108*mm]),
 p('Людина не підтверджує кожну дію NPC в реальному часі. Розробник змінює правила, а QA після гри переглядає сумнівні випадки в журналі. Пороги прийняті як попередні на основі ПР-7.',NOTE)
])

story.extend([p('7. Помилки, обмеження і розвиток',HEAD),
 p('<b>Три фактичні помилки ML:</b> запис №310 — висока загроза пропущена (0,386; confidence 0,614); №3 — загроза пропущена (0,319; confidence 0,681); №328 — хибно висока загроза (0,598; confidence 0,598). У всіх випадках слід застосувати правила й зберегти обставини для QA.'),
 p('<b>Обмеження:</b> синтетичні дані з формульними мітками; 8 із 36 високих загроз пропущені; confidence не каліброване; пороги випробувані на невеликій вибірці; немає інтеграції з рушієм, навігації та повноцінного інтерфейсу QA.'),
 p('<b>Подальші кроки:</b> зібрати реальні логи гри, покращити виявлення високої загрози й калібрувати ML; підключити C4 до рушія; реалізувати DP-08/DP-09 та C8/D4.'),
 p('8. Матеріали репозиторію',HEAD),
 p('У GitHub/GitLab слід завантажити папку з <b>README.md</b>, схемою <b>docs/architecture_final.png</b>, Notebook ПР-6, робочим кодом <b>src/npc_ai.py</b>, тестами, синтетичними даними, результатами перевірки та цим PDF.'),
 p('<b>Висновок.</b> Проєкт логічно пов’язує ПР-1–ПР-7 і має відтворюваний навчальний прототип. Його можна демонструвати та розвивати, але поки не можна назвати готовою інтегрованою системою NPC без тестування на реальних даних і в рушії.')
])

SimpleDocTemplate(str(TEMP),pagesize=A4,
    leftMargin=16*mm,rightMargin=16*mm,topMargin=16*mm,bottomMargin=15*mm,
    title='Практична робота 8 — Фінальний проєкт NPC',
    author='Дем’яненко Микола').build(story)

# Окрема A3 landscape-сторінка схеми: збільшена для читабельності під час захисту.
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
pw,ph=landscape(A3)
c=canvas.Canvas(str(ARCH),pagesize=(pw,ph))
c.setTitle('Фінальна архітектурна схема NPC')
image=ImageReader(str(R/'docs/architecture_final.png'))
iw,ih=image.getSize()
scale=min((pw-35*mm)/iw,(ph-28*mm)/ih)
dw,dh=iw*scale,ih*scale
c.drawImage(image,(pw-dw)/2,(ph-dh)/2,width=dw,height=dh)
c.showPage();c.save()

# Вставляємо схему після першої сторінки тексту.
a=fitz.open(str(TEMP));b=fitz.open(str(ARCH));out=fitz.open()
out.insert_pdf(a,from_page=0,to_page=0)
out.insert_pdf(b)
if a.page_count > 1:out.insert_pdf(a,from_page=1,to_page=a.page_count-1)
out.set_metadata({'title':'Практична робота №8 — Фінальний проєкт NPC',
                  'author':'Дем’яненко Микола'})
out.save(str(OUT),garbage=4,deflate=True)
out.close();a.close();b.close()
TEMP.unlink();ARCH.unlink()
print('CREATED',OUT,'pages',fitz.open(str(OUT)).page_count)
