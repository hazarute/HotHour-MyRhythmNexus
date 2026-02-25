# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz R3.2: User Models Refactor + Token Flow Tamam** ✅

- Yapılan: app/models/user.py sıfırdan (Prisma schema-aligned)
- Backend: Auth endpoints Token döner (access_token + user data)
- Frontend: SignUpView direkt Token kullanır (login çağrısı yok)
- Syntax: Python ✅ + Vue ✅ + Build ✅

## 📐 User Models Yeniden Mimarisi

### Prisma ↔ Pydantic Field Mappings
```
fullName     → full_name
isVerified   → is_verified
createdAt    → created_at
hashedPassword → hashed_password (backend only)
```

### Request Models (Built-in Validators)
**UserCreate:**
- email: EmailStr (Pydantic auto-validate)
- full_name: 3+ chars, letters + Turkish (regex)
- phone: 10+ rakam extracted (regex)
- gender: Enum (FEMALE | MALE)
- password: 8+ chars

**UserLogin:**
- email: EmailStr
- password: str

### Response Models (API Returns)
**UserResponse:** `{id, email, full_name, phone, gender, role, is_verified, created_at}`
**UserPublicProfile:** `{id, full_name, created_at}` (privacy)
**Token:** `{access_token, token_type, user: UserResponse}` 🆕

### Internal Models (Backend-Only)
**UserInDB:** Hashed password ile (DB operations)
**TokenData:** JWT içinden extracted {user_id, email}

## 🔐 Validasyon 3-Katmanı

1. **Frontend** (@input handlers): Real-time filtering
2. **Backend Validators** (@field_validator): Data integrity (422)
3. **Business Logic** (auth.py): Duplicate checks (400)
4. **Database**: Unique constraints

## 🔄 Backend Endpoint Changes

### Register (POST /register)
| Aspect | Before | After |
|--------|--------|-------|
| Response | UserResponse | Token {access_token, user} 🆕 |
| Flow | Register → need login | Register → auto-token |
| Duplicates | Email only | Email + Phone 🆕 |

### Login (POST /login) 
| Aspect | Before | After |
|--------|--------|-------|
| Response | {access_token, token_type} | Token {access_token, user} 🆕 |
| User Data | Separate /me call | Immediate return |

### /me (GET /me)
- Unchanged: UserResponse return

## 📝 Dosyalar Güncellendi
- ✅ [app/models/user.py](app/models/user.py) - Sıfırdan (docstrings + validators)
- ✅ [app/api/auth.py](app/api/auth.py) - Token response + field mapping
- ✅ [app/services/user_service.py](app/services/user_service.py) - get_user_by_phone()
- ✅ [frontend/src/views/SignUpView.vue](frontend/src/views/SignUpView.vue) - Token handler

## ⏭️ Sıradaki Adımlar (Test)
1. [ ] Backend sunucu başlatma (uvicorn)
2. [ ] Registration form submit via localhost
3. [ ] Token + auto-redirect doğrulama
4. [ ] Login endpoint test (existing user)
5. [ ] Error cases (duplicate email/phone, invalid data)
- [ ] Duplicate email/phone edge cases