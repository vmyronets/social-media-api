# 🌐 Social Media API - Django REST Framework

A comprehensive RESTful API for a social media platform built with Django REST Framework. This API supports user authentication, 
profiles, posts with scheduled publishing, likes, comments, and a follow/unfollow system.

## 🚀 Features

- ✅ User Registration and Authentication (Token-based via Django REST Knox)
- ✅ User Profile Management — create, update, and view profiles 
- ✅ User Search by username or other attributes
- ✅ Follow/Unfollow System
- ✅ Post Creation with text, media attachments, and hashtags 
- ✅ Scheduled Post Publishing (using Celery + Redis)
- ✅ Post Likes
- ✅ Post Comments
- ✅ Media Upload Support (user avatars, post images)
- ✅ API Documentation (Swagger UI)
- ✅ Proper Permissions — Users can manage only their own data

## 🧱 Tech Stack

- **Framework**: Django + Django REST Framework
- **Database**: PostgreSQL (or SQLite for development)
- **Authentication**: Token-based (Django REST Knox)
- **Task Queue**: Celery + Redis
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Containerization**: Docker + Docker Compose

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/vmyronets/social-media-api.git
````

### 2. Go to the project directory
```bash
cd social-media-api
```

### 3. Rename `env_sample` to `.env` and fill in the values

### 4. Build and Run Docker Containers

```bash
docker compose up --build
```

This will:
- Build the Django application image
- Start PostgreSQL database
- Start Redis server
- Start Django application
- Start Celery worker
- Start Celery beat scheduler


### 5. Create Superuser
```bash
docker compose exec app python manage.py createsuperuser
```

### 6. Access the Application

Once all services are running:

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📚 API Documentation

Swagger UI is automatically generated using `drf-spectacular` and available at:

```
http://localhost:8000/api/docs/
```

---

## 🧩 Project Structure

```
social-media-api/
├── social_media/          # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── celery.py          # Celery configuration
├── user/                  # User app
│   ├── models.py          # User, Profile, Follow models
│   ├── serializers.py     # User serializers
│   ├── views.py           # Authentication & profile views
│   └── urls.py            # User endpoints
├── content/               # Post app
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

### Content App

1. **Content**
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

## ⚡ API Endpoints

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

---

## 🏁 License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute it with attribution.

---