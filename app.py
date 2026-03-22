from flask import Flask, flash, redirect, render_template, request, session, url_for

from ai import analyze_password_ai, improve_password_ai
from config import APP_PASSWORD, APP_USER, SECRET_KEY
from utils import (
    delete_password_entry,
    evaluate_password,
    generate_password,
    get_passwords_view,
    load_data,
    password_exists,
    password_score,
    save_password_entry,
    score_color,
    score_label,
)

app = Flask(__name__)
app.secret_key = SECRET_KEY


def is_logged_in() -> bool:
    return bool(session.get("user"))


@app.route("/", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == APP_USER and password == APP_PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Неверный логин или пароль.")

    return render_template("login.html", error=None)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    generated_password = None
    generated_score = None
    generated_label = None
    generated_color = None

    check_password_value = ""
    checked_score = None
    checked_label = None
    checked_color = None

    ai_input_password = ""
    ai_local_result = None
    ai_result = None
    improved_password = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "save_entry":
            try:
                name = request.form.get("name", "").strip()
                mode = request.form.get("mode", "generate")

                if not name:
                    raise ValueError("Введите название записи.")

                if mode == "generate":
                    length = int(request.form.get("length", "12"))
                    days = int(request.form.get("days", "30"))
                    use_lower = bool(request.form.get("lower"))
                    use_upper = bool(request.form.get("upper"))
                    use_digits = bool(request.form.get("digits"))
                    use_symbols = bool(request.form.get("symbols"))

                    if length < 4:
                        raise ValueError("Длина пароля должна быть не меньше 4.")
                    if days < 1:
                        raise ValueError("Срок действия должен быть не меньше 1 дня.")

                    data = load_data()
                    generated_password = generate_password(
                        length=length,
                        use_lower=use_lower,
                        use_upper=use_upper,
                        use_digits=use_digits,
                        use_symbols=use_symbols,
                        data=data,
                    )
                    generated_score = password_score(generated_password)
                    generated_label = score_label(generated_score)
                    generated_color = score_color(generated_score)

                    save_password_entry(name, generated_password, days)
                    flash("Сгенерированный пароль успешно сохранён.", "success")

                elif mode == "manual":
                    manual_password = request.form.get("manual_password", "").strip()
                    manual_days = int(request.form.get("manual_days", "30"))

                    if not manual_password:
                        raise ValueError("Введите свой пароль.")
                    if manual_days < 1:
                        raise ValueError("Срок действия должен быть не меньше 1 дня.")

                    data = load_data()
                    if password_exists(manual_password, data):
                        raise ValueError("Такой пароль уже сохранён в системе.")

                    generated_password = manual_password
                    generated_score = password_score(manual_password)
                    generated_label = score_label(generated_score)
                    generated_color = score_color(generated_score)

                    save_password_entry(name, manual_password, manual_days)
                    flash("Ваш пароль успешно сохранён.", "success")

                else:
                    raise ValueError("Неизвестный режим сохранения.")

            except Exception as e:
                flash(str(e), "error")

        elif action == "check":
            check_password_value = request.form.get("user_password", "")
            checked_score = password_score(check_password_value)
            checked_label = score_label(checked_score)
            checked_color = score_color(checked_score)

        elif action == "analyze_ai":
            ai_input_password = request.form.get("ai_password", "").strip()
            if ai_input_password:
                ai_local_result = evaluate_password(ai_input_password)
                ai_result = analyze_password_ai(ai_input_password)
            else:
                flash("Введите пароль для AI-анализа.", "error")

        elif action == "improve_ai":
            ai_input_password = request.form.get("ai_password", "").strip()
            if ai_input_password:
                ai_local_result = evaluate_password(ai_input_password)
                improved_password = improve_password_ai(ai_input_password)
            else:
                flash("Введите пароль для AI-улучшения.", "error")

    search = request.args.get("search", "").strip()
    passwords = get_passwords_view(search if search else None)

    return render_template(
        "app.html",
        passwords=passwords,
        search=search,
        generated_password=generated_password,
        generated_score=generated_score,
        generated_label=generated_label,
        generated_color=generated_color,
        check_password_value=check_password_value,
        checked_score=checked_score,
        checked_label=checked_label,
        checked_color=checked_color,
        ai_input_password=ai_input_password,
        ai_local_result=ai_local_result,
        ai_result=ai_result,
        improved_password=improved_password,
    )


@app.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id: str):
    if not is_logged_in():
        return redirect(url_for("login"))

    delete_password_entry(entry_id)
    flash("Запись удалена.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)