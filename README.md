## Google Cloud Translate Service

Serverless service for handling translation using Google Translate API.

#### Useful Documentations:
- [Google Translate API](https://cloud.google.com/translate/docs/)
- [Google Translate Python Client](https://cloud.google.com/translate/docs/reference/libraries/v2/python)

#### Local Installation

```
git clone https://github.com/atnic/google-cloud-translate-service.git
cd google-cloud-translate-service
python -m venv env
source env/bin/activate
pip install -r requirements.txt
npm install
cp .env.example .env
```

Edit `.env` file to satisfy your environment

#### Auto Deployment

- Config Github Secret repo to setup this, see `.env` file for references
    - `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY` for production
    - `AWS_ACCESS_KEY_ID_STAGING` & `AWS_SECRET_ACCESS_KEY_STAGING` for staging
    - `AWS_ACCESS_KEY_ID_DEV` & `AWS_SECRET_ACCESS_KEY_DEV` for dev
    - `AWS_REGION`
    - `GOOGLE_APPLICATION_CREDENTIALS_JSON` for production, copy the content of json you've download from Google Cloud Console
    - `GOOGLE_APPLICATION_CREDENTIALS_JSON_STAGING` for staging
    - `GOOGLE_APPLICATION_CREDENTIALS_JSON_DEV` for dev
    - `GOOGLE_APPLICATION_CREDENTIALS`
    - `DB_TRANSLATIONS`
- After you setup secret
    - Commit to `master` branch will go to prod
    - Commit to `release/*` branch will go to staging
    - Commit to `develop` branch will go to dev

#### Manual Production Deployment

- Make sure you already have profile defined in `.aws/credentials` where you want to deploy to.
- **Make sure you're on `master` branch**
- Edit your `.env` to satisfy production environment
- Then run
```
serverless deploy --aws-profile [your-profile] --stage prod
```
- Don't forget to add it to your API Gateway if you use it.
