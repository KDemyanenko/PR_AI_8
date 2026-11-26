"""Фінальна схема без кольорового декору; SVG та PNG."""
from pathlib import Path
import svgwrite
import cairosvg

R = Path(__file__).resolve().parents[1]
W,H=1720,1470
s=svgwrite.Drawing(str(R/'docs/architecture_final.svg'),size=(f'{W}px',f'{H}px'),viewBox=f'0 0 {W} {H}')
s.add(s.rect(insert=(0,0),size=(W,H),fill='white'))
marker=s.marker(id='arrow',insert=(9,4.5),size=(10,10),orient='auto',markerUnits='strokeWidth')
marker.add(s.path(d='M 0 0 L 9 4.5 L 0 9 z',fill='black'))
s.defs.add(marker)

def write(x,y,txt,size=22,bold=False,anchor='middle'):
    s.add(s.text(txt,insert=(x,y),text_anchor=anchor,
                 font_family='DejaVu Sans',font_size=size,
                 font_weight='bold' if bold else 'normal',fill='black'))

def box(x,y,w,h,lines,border=1.5,rounded=12,first_bold=True):
    s.add(s.rect(insert=(x,y),size=(w,h),rx=rounded,ry=rounded,
                 fill='white',stroke='black',stroke_width=border))
    fs=22 if len(lines)<=2 else 20
    dy=29
    sy=y + h/2 - (len(lines)-1)*dy/2 + 7
    for i,line in enumerate(lines):
        write(x+w/2,sy+i*dy,line,fs,first_bold and i==0)

def arrow(points,label=None,label_xy=None,dashed=False):
    p=s.polyline(points=points,fill='none',stroke='black',stroke_width=2.0,
                 marker_end=marker.get_funciri())
    if dashed:p['stroke_dasharray']='7 5'
    s.add(p)
    if label and label_xy:write(*label_xy,label,size=17)

def cylinder(x,y,w,h,lines):
    s.add(s.rect(insert=(x,y+14),size=(w,h-28),fill='white',stroke='black',stroke_width=1.5))
    s.add(s.ellipse(center=(x+w/2,y+14),r=(w/2,14),fill='white',stroke='black',stroke_width=1.5))
    s.add(s.path(d=f'M{x},{y+h-14} A{w/2},14 0 0,0 {x+w},{y+h-14}',fill='none',stroke='black',stroke_width=1.5))
    for i,line in enumerate(lines):write(x+w/2,y+h/2+(i-(len(lines)-1)/2)*25+6,line,19,i==0)

write(W/2,49,'Фінальна архітектура системи керування NPC',31,True)
write(W/2,84,'ПР-1–ПР-7: джерела даних → компоненти → ШІ → рішення → реакція',19)

# actors, engine and 8 components
box(85,133,300,82,['Гравець','ініціює подію'],rounded=38)
box(470,133,350,82,['Ігровий рушій','події / виконання дій'])

x=610;w=570;h=98
C={i:260+(i-1)*153 for i in range(1,8)}
labels={
 1:['C1. Інтеграція з рушієм','приймає події, повертає команди'],
 2:['C2. Менеджер стану NPC','HP, позиція, поточний стан'],
 3:['C3. Сприйняття ігрового світу','відстань, видимість, укриття'],
 4:['C4. Компонент ШІ (ML)','threat_score, confidence, рекомендація'],
 5:['C5. Планувальник поведінки','DP-07: чи відступати; DP-08: куди'],
 6:['C6. Навігація','маршрут та досяжність, DP-09'],
 7:['C7. Перевірка правил та обмежень','дозвіл дії, перевірка DP-07 / DP-09'],
}
for i in range(1,8):box(x,C[i],w,h,labels[i],border=2.5 if i==4 else 1.5)

# core arrows labelled outside the spine
arrow([(385,174),(470,174)],'дія гравця',(425,122))
arrow([(645,215),(645,237),(895,237),(895,260)],'стан / події',(786,228))
core_labels=['подія NPC','стан і позиція','ознаки для ML','score, confidence','ціль після DP-07','маршрут / DP-09']
for i in range(1,7):
    start=C[i]+h; end=C[i+1]
    arrow([(x+w/2,start),(x+w/2,end)],core_labels[i-1],(x+w/2+210,(start+end)/2+5))

# data stores placed aside, no crossed edges
cylinder(85,C[2]+8,350,83,['D2. Поточні стани NPC'])
arrow([(610,C[2]+49),(435,C[2]+49)],'оновлення',(525,C[2]+35))
cylinder(85,C[4]+8,350,83,['D3. Параметри моделі'])
arrow([(435,C[4]+49),(610,C[4]+49)],'завантаження',(525,C[4]+36))
cylinder(85,C[7]+8,350,83,['D1. Правила й пороги'])
arrow([(435,C[7]+49),(610,C[7]+49)],'обмеження',(525,C[7]+36))

# external nav service & human/QA sidebar
box(1270,C[6]+8,370,83,['Навігація рушія','зовнішній сервіс'])
arrow([(1180,C[6]+38),(1270,C[6]+38)],'запит',(1224,C[6]+29))
arrow([(1270,C[6]+77),(1180,C[6]+77)],'відповідь',(1226,C[6]+96))
box(1440,700,225,87,['Розробник / QA','перегляд після гри'],rounded=38)
box(1270,C[7]+8,370,83,['C8. Моніторинг і правила','черга QA, журнал подій'])
arrow([(1552,787),(1690,787),(1690,C[7]+49),(1640,C[7]+49)],'політики / аналіз',(1604,931))
arrow([(1180,C[7]+50),(1270,C[7]+50)],'запис',(1224,C[7]+34))
cylinder(1270,1362,370,80,['D4. Журнал рішень / QA'])
arrow([(1455,C[7]+91),(1455,1362)],'збереження',(1551,1348))

# actor result & fallback notes
arrow([(895,C[7]+h),(895,1384),(580,1384)],'дозволена команда до C1 / рушія',(733,1364))
box(130,1340,450,92,['Результат','дія NPC у грі / безпечна зупинка'])
arrow([(580,1384),(580,1385)],None,None)
write(85,1278,'Резерв: C4 недоступний → правило HP ≤ 25%',16,False,'start')
write(85,1305,'За 0,65–0,79 → правило HP + журнал QA',16,False,'start')

s.save()
cairosvg.svg2png(url=str(R/'docs/architecture_final.svg'),write_to=str(R/'docs/architecture_final.png'),output_width=2580,output_height=2205)
print('arch image built', R/'docs/architecture_final.png')
