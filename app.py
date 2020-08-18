import subprocess

from flask import Flask, jsonify, render_template, send_file


app = Flask(__name__)
process = None
last_progress = 0


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/download')
def download():
    return send_file(
        'data/output_multiple_season.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml'
                 '.sheet',
    )


@app.route('/teams/<home_team>/vs/<away_team>')
def teams(home_team, away_team):
    global process, last_progress

    try:
        process = subprocess.Popen(
            ['python', 'model.py', '--home', home_team, '--away', away_team],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        status = True
        last_progress = 100
    except Exception as e:
        print(e)
        status = False

    return jsonify({
        'status': status,
    })


@app.route('/teams/status')
def teams_status():
    global process, last_progress

    output = process.stdout.readline().strip()

    if 'progress' in output:
        last_progress = int(output.split(' ')[1])
        return jsonify({
            'current': last_progress
        })
    elif 'result' in output:
        _, home_score, away_score = output.split(' ')

        return jsonify({
            'current': 100,
            'result': {
                "home": home_score,
                "away": away_score,
            }
        })

    return jsonify({
        'current': last_progress
    })


if __name__ == '__main__':
    app.run(debug=True)
