# Localization (i18n) Guide

This document describes the localization implementation in EduSphere using Vue I18n.

## Overview

EduSphere now supports multiple languages through Vue I18n internationalization plugin. Users can select their preferred language from their profile settings, and the application will display content in that language.

## Supported Languages

- **English (en)** - Default language
- **Latvian (lv)** - Latviešu valoda

## Architecture

### Backend

The backend stores user language preferences in the `User` model:

```python
# backend/core/models.py
class User(AbstractBaseUser, PermissionsMixin):
    # ... other fields ...
    language = models.CharField(
        max_length=2, 
        choices=[('en', 'English'), ('lv', 'Latvian')], 
        default='en', 
        blank=True
    )
```

The language field:
- Uses ISO 639-1 two-letter language codes
- Has validation through Django choices
- Defaults to 'en' (English)
- Is exposed through GraphQL API

### Frontend

#### Structure

```
frontend/src/
├── i18n.ts                    # i18n configuration
├── locales/
│   ├── en.json               # English translations
│   └── lv.json               # Latvian translations
└── composables/
    └── useLocale.ts          # Language management composable
```

#### Translation Files

Translation files are structured JSON objects with nested keys:

```json
{
  "common": {
    "welcome": "Welcome",
    "login": "Login",
    ...
  },
  "auth": {
    "email": "Email",
    "password": "Password",
    ...
  },
  ...
}
```

## Usage

### Using Translations in Components

#### Composition API (Recommended)

```vue
<template>
  <div>
    <h1>{{ t('common.welcome') }}</h1>
    <button>{{ t('common.login') }}</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
```

#### With Parameters

```vue
<template>
  <p>{{ t('message.greeting', { name: userName }) }}</p>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const userName = ref('John');
</script>
```

Translation file:
```json
{
  "message": {
    "greeting": "Hello, {name}!"
  }
}
```

### Switching Languages

Users can change their language preference in the profile settings:

1. Navigate to their profile
2. Click "Edit Profile"
3. Select desired language from the dropdown
4. Save changes

The language preference is:
- Saved to the database via GraphQL mutation
- Automatically applied on next login
- Synced across devices

### Programmatic Language Change

```typescript
import { useLocale } from '@/composables/useLocale';

const { setLocale, currentLocale, availableLocales } = useLocale();

// Change language
setLocale('lv');

// Get current language
console.log(currentLocale.value); // 'lv'

// Get available languages
console.log(availableLocales); // ['en', 'lv']
```

## Adding New Languages

### 1. Backend

Add the language to the User model choices:

```python
# backend/core/models.py
LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('lv', 'Latvian'),
    ('es', 'Spanish'),  # New language
]
```

Create a migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Frontend

Create a new translation file:

```bash
# Create translation file
touch frontend/src/locales/es.json
```

Add translations:
```json
{
  "common": {
    "welcome": "Bienvenido",
    "login": "Iniciar sesión",
    ...
  },
  ...
}
```

Update i18n configuration:

```typescript
// frontend/src/i18n.ts
import es from './locales/es.json';

const i18n = createI18n({
  // ...
  messages: {
    en,
    lv,
    es  // Add new language
  }
});
```

Update language selector in UserProfile.vue:

```typescript
function getLanguageName(locale: string): string {
  const languageNames: Record<string, string> = {
    'en': 'English',
    'lv': 'Latviešu (Latvian)',
    'es': 'Español (Spanish)'  // Add new language
  };
  return languageNames[locale] || locale;
}
```

## Best Practices

### 1. Translation Key Naming

Use descriptive, hierarchical keys:
- ✅ `auth.login.emailPlaceholder`
- ❌ `login1`

### 2. Organize by Feature

Group related translations:
```json
{
  "room": {
    "create": "Create Room",
    "join": "Join Room",
    "leave": "Leave Room"
  }
}
```

### 3. Pluralization

Use Vue I18n's built-in pluralization:
```json
{
  "message": {
    "items": "no items | one item | {count} items"
  }
}
```

Usage:
```vue
{{ t('message.items', count) }}
```

### 4. Date and Number Formatting

Use Vue I18n's formatting utilities:
```typescript
import { useI18n } from 'vue-i18n';

const { d, n } = useI18n();

// Format date
d(new Date(), 'short')

// Format number
n(1234.56, 'currency')
```

## Testing

### Backend Tests

Language field is tested through existing user mutation tests:

```bash
python manage.py test backend/core
```

### Frontend Tests

To test i18n integration:

1. Build the application:
```bash
cd frontend
npm run build
```

2. Check for TypeScript errors:
```bash
npm run type-check
```

## Troubleshooting

### Language Not Changing

1. Check browser console for errors
2. Verify user's language field in database
3. Clear browser cache and localStorage
4. Ensure translation keys exist in both language files

### Missing Translations

If a key is missing, Vue I18n will:
1. Display the key itself (e.g., `auth.login.title`)
2. Log a warning in development mode

To fix:
1. Add the missing key to all translation files
2. Rebuild the application

### Translation Keys Not Working

Ensure you're using the correct syntax:
```vue
<!-- Correct -->
{{ t('common.welcome') }}
{{ $t('common.welcome') }}

<!-- Incorrect -->
{{ t.common.welcome }}
```

## API Reference

### useLocale Composable

```typescript
const {
  currentLocale,      // Ref<string> - Current locale code
  availableLocales,   // string[] - Array of available locales
  setLocale,         // (locale: string) => void - Change locale
  initializeLocale   // () => void - Initialize from user preference
} = useLocale();
```

### GraphQL API

#### Query User Language

```graphql
query GetUser {
  me {
    id
    username
    language
  }
}
```

#### Update User Language

```graphql
mutation UpdateUser($language: String) {
  updateUser(language: $language) {
    user {
      id
      username
      language
    }
  }
}
```

## Resources

- [Vue I18n Documentation](https://vue-i18n.intlify.dev/)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [Django Model Field Choices](https://docs.djangoproject.com/en/stable/ref/models/fields/#choices)
