# Railway Deployment Guide

## Changes Made for Railway Deployment

1. **Created `Procfile`** - Tells Railway how to start your Django app
2. **Added `gunicorn`** to requirements.txt - Production WSGI server
3. **Added `whitenoise`** to requirements.txt - Serves static files in production
4. **Updated `ALLOWED_HOSTS`** in settings.py - Now includes Railway domains
5. **Created `railway.toml`** - Railway configuration file
6. **Created `runtime.txt`** - Specifies Python version
7. **Fixed Windows-specific packages** - Made them conditional to avoid Linux build errors

## Steps to Deploy on Railway

### 1. Push Your Code to GitHub
```bash
git init
git add .
git commit -m "Prepare for Railway deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect Django and deploy

### 3. Set Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this
DJANGO_DEBUG=False
PORT=8000
```

**Important:** Generate a secure SECRET_KEY. You can use this Python command:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run Migrations

In Railway dashboard, go to Settings → Deploy → Click "Deploy" to trigger a deployment.

After deployment, you can run migrations by:
- Going to the service → Settings → Add a new "One-off Command"
- Run: `python manage.py migrate`

Or use Railway CLI:
```bash
railway run python manage.py migrate
```

### 5. Create Superuser (Optional)

To access Django admin, create a superuser:
```bash
railway run python manage.py createsuperuser
```

### 6. Collect Static Files

Static files should be collected automatically, but if needed:
```bash
railway run python manage.py collectstatic --noinput
```

## Troubleshooting

### Build Fails
- Check the build logs in Railway dashboard
- Make sure all dependencies are in requirements.txt
- Verify Python version in runtime.txt matches your local version

### App Won't Start
- Check deploy logs for errors
- Verify environment variables are set correctly
- Make sure ALLOWED_HOSTS includes your Railway domain

### Static Files Not Loading
- Verify WhiteNoise is in MIDDLEWARE
- Run `python manage.py collectstatic --noinput`
- Check that STATIC_ROOT is set correctly

### Database Issues
- Railway uses SQLite by default (file-based)
- For production, consider PostgreSQL:
  - Add Railway PostgreSQL service
  - Update DATABASE settings in settings.py
  - Add `psycopg2-binary` to requirements.txt

## Production Database (PostgreSQL) - Recommended

SQLite is not recommended for production. To use PostgreSQL:

1. In Railway, add a PostgreSQL database to your project
2. Railway will automatically add DATABASE_URL environment variable
3. Update settings.py to use DATABASE_URL:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

4. Add to requirements.txt:
```
dj-database-url==2.1.0
psycopg2-binary==2.9.9
```

## Your Railway URLs

Once deployed, Railway will provide:
- **Public URL**: https://your-app-name.up.railway.app
- This URL is automatically added to ALLOWED_HOSTS

## Need Help?

- Railway Docs: https://docs.railway.app
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

