# Як опублікувати фінальний проєкт на GitHub

Це **локально підготовлений репозиторій**, не опублікований автоматично. Посилання на GitHub з’явиться лише після завантаження файлів у **ваш** акаунт.

## Спосіб 1 — через сайт GitHub

1. Увійдіть у свій обліковий запис на [github.com](https://github.com/).
2. Створіть новий репозиторій, наприклад `npc-ai-behavior`. Не потрібно автоматично додавати другий README, бо `README.md` вже входить у проєкт.
3. Розпакуйте ZIP-архів фінального проєкту.
4. На сторінці репозиторію виберіть **Add file → Upload files** та завантажте **вміст папки `NPC_AI_Final_Project`**, зберігаючи підпапки `src`, `docs`, `data`, `results`, `notebooks`, `scripts`, `tests`.
5. Зробіть коміт, відкрийте README та переконайтеся, що схема відображається.
6. Скопіюйте адресу саме вашого репозиторію і додайте її в Classroom разом із файлом `PR8_Final_Report.pdf`.

## Спосіб 2 — через Git

Створіть порожній репозиторій на GitHub, потім у терміналі, **всередині папки** `NPC_AI_Final_Project`:

```bash
git init
git add .
git commit -m "Final NPC AI project PR1-PR8"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГІН/npc-ai-behavior.git
git push -u origin main
```

Замініть `ВАШ_ЛОГІН` на свій GitHub-логін і назву репозиторію за потреби. Команди вимагають входу до GitHub та встановленого Git.

## Що саме здати

- **Посилання на живий репозиторій GitHub/GitLab**, а не посилання на ZIP у ChatGPT.
- **Один фінальний PDF** із папки `docs/PR8_Final_Report.pdf`.

## Перевірка перед здачею

- [ ] README видно на головній сторінці репозиторію.
- [ ] Відкривається схема `docs/architecture_final.png`.
- [ ] Є `notebooks/PR6_NPC_Prototype.ipynb`.
- [ ] Є робочий код у `src/npc_ai.py`.
- [ ] Є результати в `results/`.
- [ ] Команди запуску з README працюють.
- [ ] У Classroom додано **посилання на репозиторій** і PDF.
