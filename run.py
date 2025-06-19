from app import app

if __name__ == '__main__':
    print("🌍 Starting Environmental Guardian Game...")
    print("📍 Open your browser and go to: http://127.0.0.1:5000")
    print("🎮 Have fun saving the planet!")
    app.run(debug=True, host='127.0.0.1', port=5000)
