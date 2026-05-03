from app import create_app

app = create_app("development")

if __name__ == "__main__":
    with app.app_context():
        from app.seeds import seed_db
        seed_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
