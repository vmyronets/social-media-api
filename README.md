# Social Media API - Django REST Framework

A comprehensive RESTful API for a social media platform built with Django REST Framework. This API supports user authentication, 
profiles, posts with scheduled publishing, likes, comments, and a follow/unfollow system.

## Features

- ✅ User Registration and Authentication (Token-based)
- ✅ User Profile Management
- ✅ User Search
- ✅ Follow/Unfollow System
- ✅ Post Creation with hashtags
- ✅ Scheduled Post Publishing (using Celery)
- ✅ Post Likes
- ✅ Post Comments
- ✅ Media Upload Support (images)
- ✅ API Documentation (Swagger UI)
- ✅ Proper Permissions

## Tech Stack

- **Framework**: Django 5.2.7 + Django REST Framework 3.16.1
- **Database**: SQLite
- **Authentication**: Token-based (Django REST Knox)
- **Task Queue**: Celery 5.5.3 + Redis
- **API Documentation**: drf-spectacular (OpenAPI 3.0)

## Project Structure

```
backend/
├── social_media/          # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── celery.py          # Celery configuration
├── user/                  # User app
│   ├── models.py          # User, Profile, Follow models
│   ├── serializers.py     # User serializers
│   ├── views.py           # Authentication & profile views
│   └── urls.py            # User endpoints
├── post/                  # Post app
│   ├── models.py          # Post, Hashtag, Like, Comment models
│   ├── serializers.py     # Post serializers
│   ├── views.py           # Post views
│   ├── tasks.py           # Celery tasks for scheduled posts
│   ├── signals.py         # Post signals
│   └── urls.py            # Post endpoints
└── manage.py              # Django management script
```

## Models

### User App

1. **User** (extends AbstractUser)
   - username, email, password, first_name, last_name

2. **Profile**
   - user (OneToOne to User)
   - nickname
   - bio
   - avatar (ImageField)

3. **Follow**
   - follower (FK to User)
   - following (FK to User)
   - created_at

### Post App

1. **Post**
   - author (FK to User)
   - text
   - scheduled_time (nullable)
   - image (ImageField, nullable)
   - hashtag (ManyToMany to Hashtag)
   - created_at
   - updated_at
   - is_published (auto-managed)

2. **Hashtag**
   - name
   - posts (ManyToMany to Post)

3. **Like**
   - user (FK to User)
   - post (FK to Post)
   - created_at

4. **Comment**
   - author (FK to User)
   - post (FK to Post)
   - text
   - created_at
   - updated_at

## API Endpoints

### Authentication Endpoints

```
POST /api/auth/register/          - Register a new user
POST /api/auth/login/             - Login and get token
POST /api/auth/logout/            - Logout (invalidate token)
```

### Profile Endpoints

```
GET  /api/auth/profile/me/        - Get current user's profile
PUT  /api/auth/profile/me/update/ - Update current user's profile
GET  /api/auth/profiles/          - List all profiles
GET  /api/auth/profiles/{id}/     - Get specific profile
```

### User Search

```
GET  /api/auth/users/search/?search=keyword  - Search users
```

### Follow/Unfollow Endpoints

```
POST /api/auth/follow/            - Follow a user (body: {\"following_id\": <user_id>})
POST /api/auth/unfollow/          - Unfollow a user (body: {\"following_id\": <user_id>})
GET  /api/auth/following/         - List users you're following
GET  /api/auth/followers/         - List your followers
```

### Post Endpoints

```
GET    /api/posts/                - List all published posts
POST   /api/posts/                - Create a new post
GET    /api/posts/{id}/           - Get specific post
PUT    /api/posts/{id}/           - Update post (author only)
DELETE /api/posts/{id}/           - Delete post (author only)
GET    /api/posts/my/             - Get current user's posts
GET    /api/posts/feed/           - Get posts from followed users
GET    /api/posts/?hashtag=name   - Filter posts by hashtag
```

### Like Endpoints

```
GET  /api/likes/                  - List all likes
POST /api/like/                   - Like a post (body: {\"post_id\": <post_id>})
POST /api/unlike/                 - Unlike a post (body: {\"post_id\": <post_id>})
GET  /api/likes/my/               - Get posts you've liked
```

### Comment Endpoints

```
GET    /api/comments/             - List all comments
POST   /api/comments/             - Create a comment
GET    /api/comments/{id}/        - Get specific comment
PUT    /api/comments/{id}/        - Update comment (author only)
DELETE /api/comments/{id}/        - Delete comment (author only)
GET    /api/comments/my/          - Get your comments
GET    /api/comments/?post_id=id  - Filter comments by post
```

### Hashtag Endpoints

```
GET  /api/hashtags/               - List all hashtags
GET  /api/hashtags/{id}/          - Get specific hashtag
GET  /api/hashtags/{id}/posts/    - Get posts with this hashtag
```

### API Documentation

```
GET  /api/docs/                   - Swagger UI (Interactive API docs)
GET  /api/schema/                 - OpenAPI schema
```

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Services**

   The project uses Supervisor to manage services:
   ```bash
   # Start Redis
   sudo supervisorctl start redis
   
   # Start Celery Worker
   sudo supervisorctl start celery_worker
   
   # Start Celery Beat (for scheduled posts)
   sudo supervisorctl start celery_beat
   
   # Start Django
   python manage.py runserver 0.0.0.0:8001
   ```

