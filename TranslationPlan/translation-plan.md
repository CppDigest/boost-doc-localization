## Translation Discussion

**Browser translation is inconsistent.** The same page shows different translations in different browsers. Chrome, Firefox, and Edge produce different results. The translation also changes between browser versions. Custom translation logic keeps technical terms consistent and validates translations against technical rules.

**English proficiency varies by region.** Many Chinese developers have limited English reading ability. Technical English is harder than basic English. Reading documentation in English takes more time and causes mistakes. Translation logic helps non-native speakers understand concepts faster while maintaining accuracy through controlled translation.

**Browser translation requires user action.** Users must find and enable the translation feature. Many users do not know this feature exists. Some users cannot access it due to workplace restrictions. Translation logic provides native multilingual docs automatically. Users do not need to enable browser features.

**Translation quality is unpredictable.** Browser tools cannot maintain consistent technical terms. They often mistranslate code-related words. They break code examples by translating variable names. Custom logic includes review workflows and terminology databases for Boost-specific terms. It does not translate code examples. It applies validation rules for technical content.

**Community growth matters.** A multilingual site removes language barriers. More developers worldwide can join Boost. The community grows beyond English-speaking regions.

**Simple English foundation works better.** Translation logic works with simple English source docs. Better English helps both native and non-native speakers. Simple English produces better translations. The system does not replace English as the technical language.

---

## Translation Requirements

**1. Content Translation Scope:** Translate static documentation from S3 buckets (library docs, user guides, API references, code examples). Translate database content (library descriptions, category names, news entries, release notes). UI elements stay in English for current version.

**2. Routing Implementation:** Implement language selection method. URL prefix approach recommended for SEO. Detect user language from browser settings or geo-location. Provide language dropdown for manual switching. Save preference in cookies.

**3. Translation System Logic:** Build terminology database for Boost-specific terms. Preserve code examples untranslated. Implement fallback to English for missing translations. Store translations in database using separate columns or JSONB fields. Organize S3 files with language prefix folders.

**4. Quality Control Process:** Create validation rules for technical accuracy. Setup review workflow with domain experts. Track translation status and coverage. Monitor error reports from users. Maintain consistency across all translated content.

---

## Implementation Approach

### UI Elements Translation

**Django i18n Framework** - Proper internationalization uses Django's i18n system.

**Current Status:** The existing UI can remain with static English text for now. Retrofitting the current codebase with i18n would require excessive refactoring time. The priority is translating documentation and database content first.

**Future Requirement:** The next major UI version must be designed with internationalization from the start. All text strings must use translation functions. No hardcoded text in code. This is essential for proper multilingual support. Without this foundation, UI translation remains manual and error-prone.

### Language Selection Methods

**Approach 1: URL Prefix** (`/en/`, `/zh/`) - SEO-friendly with separate URLs per language. Django natively supports this. Users can bookmark and share language-specific links. Requires URL structure changes and redirects for old URLs.

**Approach 2: Cookie/Session** - Same URL serves different content based on cookie. No URL changes needed. Existing bookmarks work. Poor for SEO. Cannot share language-specific URLs.

**Approach 3: Subdomain** (`en.boost.org`, `zh.boost.org`) - Clean separation per language. Excellent for CDN caching and SEO. Scales independently. Requires complex infrastructure with multiple SSL certificates and higher costs.

### Database Translation Methods

**Approach 1: Separate Columns** (`description_en`, `description_zh`) - Django package django-modeltranslation adds language columns. Fast queries with automatic admin interface. Requires schema changes and new migrations for each language. Many additional columns.

**Approach 2: JSONB Field** (`{"en": "text", "zh": "text"}`) - Single flexible field stores all languages. No schema changes when adding languages. Can store metadata like translator and date. Requires custom admin interface and more complex queries.

**Approach 3: Separate Translation Table** - Foreign key links translations to main content. Professional workflow with translator tracking. Easy export for translation services. Scales well with many languages. Requires joins and more complex code.

### Static Files Methods

**Approach 1: Language Prefix Folders** (`/en/doc/`, `/zh/doc/`) - Simple structure with clear separation. CDN-friendly caching. Independent language updates. Easy to navigate. Requires storage duplication and manual synchronization.

**Approach 2: Separate Buckets** (`boost-static-en`, `boost-static-zh`) - Complete isolation per language. Fine-grained access control. Teams own their buckets. Geo-optimization possible. Multiple buckets increase costs and operational overhead.

**Approach 3: Metadata-Driven** - Language in filename (`index.html.zh`) or S3 metadata. Storage efficient with rich tracking. Automated gap detection. Requires Lambda@Edge and complex routing logic.

### AI Translation Integration

**Approach 1: Admin Button** - Admin starts translation by clicking "Translate" button. Human reviews before saving. Fast with human oversight. Reduces workload by 70-80%. Needs custom admin development.

**Approach 2: Automatic Background** - When content is saved to database, AI translates automatically using Celery workers. Fully automatic and scalable. Requires Celery and Redis setup.

**Approach 3: Manual Command** - Run CLI command when ready. Shows preview before translating. Full control over timing and costs. Simple to implement. Requires manual execution.

---
