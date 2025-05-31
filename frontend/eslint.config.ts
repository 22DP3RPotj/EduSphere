import js from '@eslint/js'
import globals from 'globals'
import vue from 'eslint-plugin-vue'
import typescriptEslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'
import vueParser from 'vue-eslint-parser'

export default [
  {
    ignores: ['**/node_modules/**', '**/dist/**', '**/*.d.ts'],
  },
  {
    files: ['**/*.{ts,js,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: '@typescript-eslint/parser',
        project: './tsconfig.json',
        ecmaVersion: 2024,
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
      globals: {
        ...globals.browser,
      },
    },
    plugins: {
      vue,
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
    },
  },
  js.configs.recommended,
  ...typescriptEslint.configs.recommended,
  ...vue.configs['flat/recommended'],
  prettier,
]
