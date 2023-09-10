import yaml

def getCredentialsSteam():
    with open('../../credentials/credentialsSteam.yml') as f:
        data = yaml.safe_load(f)
        return (data['USERNAME'], data['PASSWORD'])