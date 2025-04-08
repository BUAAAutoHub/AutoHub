import subprocess
def validate_token(token):
    headers = {'Authorization': 'token ' + token, 'Content-Type': 'application/json; charset=utf-8'}
    response = requests.get('https://api.github.com/user', headers=headers)
    print(token, response.status_code)
    if response.status_code == 200:
        return True
    print("Response body:", response.text)
    print("Response headers:", response.headers)
    return False

if __name__ == "__main__":
    token="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"
    command = ['gh', 'api', '-H', 'Accept: application/vnd.github.v3+json', '-H', 'Authorization: token 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', '/repos/BUAAAutoHub/AutoHub']
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd="/home/auto/AutoHub/backend/userRepos/user2/AutoHub", check=True)
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Command failed with exit code:", e.returncode)
        print("Output:", e.output)
        print("Error:", e.stderr)
        raise