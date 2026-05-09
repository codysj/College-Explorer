

College Exploration Platform
Final Project Spec for LLM Implementation

Optimized for: Big Tech SWE resume signal with slight quant/data infrastructure emphasis
Version: May 2026
Project thesis:
A full-stack decision engine that helps prospective and admitted students discover, compare, rank, and justify college choices using structured data, semantic matching, explainable scoring, and cost/value tradeoff analysis.
 
Manual Table of Contents
•	1. Executive Spec Brief
•	2. Product Definition and User Problem
•	3. LLM Implementation Protocol
•	4. Final Product Surface and UX System
•	5. Technical Stack and Architecture
•	6. Data Model and Data Pipeline
•	7. Ranking, Search, and Decision Logic
•	8. V1 Roadmap: Production-Quality MVP
•	9. V2 Roadmap: Recommendation and Decision Intelligence
•	10. V3 Roadmap: Production Hardening and Portfolio Polish
•	11. API Contract Outline
•	12. Testing, Observability, and Security Gates
•	13. Resume Positioning and Demo Strategy
•	14. Appendices: Build Prompts, Data Dictionary, References
This table of contents is intentionally static so the document renders reliably across Word, Google Docs, and LibreOffice.
 
1. Executive Spec Brief
1.1 One-sentence definition
College Exploration Platform is a personalized college decision platform that helps students move from an overwhelming set of schools to a confident, explainable shortlist or final enrollment choice.
1.2 Resume-optimized framing
This project should be framed as a consumer-scale full-stack system, not as a generic college directory. The strongest technical signals are: indexed search, ranking infrastructure, semantic retrieval, Redis caching, PostgreSQL/pgvector, cloud deployment, user accounts, performance measurement, and real-user product workflows.
1.3 Target resume gap
Area	Spec detail	Deliverable
Gap	How this project fills it	Proof artifact to create
Consumer-scale product	Shows real users, UX, account workflows, and a practical decision problem.	Landing page, onboarding, saved lists, user metrics.
Backend systems depth	Demonstrates query optimization, caching, pagination, indexing, API design, and performance gates.	README architecture diagram, p95 before/after chart, load test summary.
Search/ranking infra	Shows retrieval, scoring, personalization, pgvector, explainability, and versioned ranking formulas.	Ranking doc, scorer tests, sample ranked outputs.
Data/product judgment	Shows the ability to convert messy college attributes into useful consumer decisions.	Decision report, comparison workflow, cost/value logic.
Slight quant signal	Adds weighted scoring, sensitivity analysis, cost modeling, and ROI-style comparisons without making the project purely finance.	Sensitivity dashboard and cost-adjusted ranking.

1.4 Product pillars
•	Discovery: help students find schools using filters, semantic search, similar-school recommendations, and preference onboarding.
•	Personalized ranking: score schools against academic, career, cost, location, admissions, and campus-life preferences.
•	Decision support: compare schools, enter acceptance/aid data, analyze tradeoffs, and generate a shareable decision report.
•	Trust and explainability: every recommendation must explain why it matches and what tradeoffs the student is accepting.
1.5 Non-negotiable success criteria
•	The project must be demoable in under 90 seconds by a recruiter: onboarding -> ranked schools -> compare -> decision report.
•	The backend must expose real APIs rather than static mock data for core search and ranking flows.
•	The README must include architecture, local setup, performance metrics, known limitations, and screenshots/GIFs.
•	The ranking logic must be deterministic and testable. LLMs may enhance copy later, but should not own the core decision logic.
•	The platform must avoid pretending to be admissions or financial advice. It is a decision-support and exploration tool.
2. Product Definition and User Problem
2.1 Primary users
User	Core problem	Product response
High school junior	Does not know where to apply.	Needs discovery, fit signals, reach/target/likely balance, and list-building.
High school senior with acceptances	Has offers but cannot decide where to enroll.	Needs comparison, cost/value tradeoffs, decision confidence, and parent-friendly explanations.
Parent or counselor	Needs a concise rationale and cost clarity.	Needs shareable reports, transparent metrics, and risk flags.

2.2 Core jobs-to-be-done
•	When I am building my college list, help me find schools that fit my academic, financial, career, and lifestyle priorities.
•	When I have too many possible schools, help me narrow them into reach, target, likely, and finalist lists.
•	When I am choosing between acceptances, help me understand the real tradeoffs across cost, outcomes, culture, and personal fit.
•	When I talk with parents or counselors, give me a clear, evidence-based explanation for why certain schools are on top.
2.3 Pain points the platform should solve
Pain point	Why it matters	Feature response
Information overload	College data is scattered and hard to compare.	Unified school profiles, filtered search, structured comparison.
Weak personalization	Ranking lists are generic and do not reflect the student.	Preference quiz, weighted ranking, editable weights.
Unclear tradeoffs	Students over-index on prestige or anecdotal opinions.	Fit breakdown, cost/value analysis, sensitivity testing.
Poor decision workflow	Existing tools help search but not finalize.	Acceptance decision mode, shareable decision report.
Trust issues	Black-box recommendations feel arbitrary.	Explainable scoring and source-aware attributes.

2.4 Product non-goals
•	Do not build a full admissions predictor as the primary product. Admissions odds are noisy, ethically sensitive, and can distract from fit.
•	Do not build a social network or forum in V1 or V2. It adds moderation burden and weakens the core engineering story.
•	Do not rely on an LLM to hallucinate college facts. Structured data is the source of truth.
•	Do not scrape private student-review sites or bypass terms of service.
•	Do not optimize for every possible college attribute. Prioritize attributes that improve actual student decisions.
3. LLM Implementation Protocol
3.1 How an LLM builder should use this spec
This spec is written so an LLM agent can implement the project in staged, verifiable increments. Each implementation prompt should be self-contained, should ask the agent to inspect the current repository before editing, and should require tests plus documentation updates before completion.
3.2 Standard build loop for every step
1.	Read relevant docs first: README, AGENTS.md, architecture notes, task tracker, database schema, API docs, and frontend route map.
2.	Inspect the current repository state before proposing changes.
3.	Implement the smallest coherent slice of functionality for the current step.
4.	Add or update tests at the correct layer: unit, integration, API, frontend component, or end-to-end smoke tests.
5.	Run validation commands and fix failures before summarizing work.
6.	Update documentation: README, API docs, schema notes, task tracker, and screenshots checklist where relevant.
7.	Summarize changed files, tests run, remaining risks, and suggested next task.
3.3 LLM guardrails
•	Never build V2 features before V1 data, search, profiles, and ranking are stable.
•	Never replace deterministic scoring with unconstrained LLM output.
•	Never ship fake performance metrics. If real metrics are unavailable, mark them as placeholders or omit them.
•	Never store sensitive applicant details unless the user explicitly enters them and the app has clear privacy boundaries.
•	Never make claims like guaranteed admissions, guaranteed ROI, or definitive financial advice.
•	Prefer typed contracts, fixtures, seed data, and tests over one-off UI mockups.
3.4 Definition of done for any feature
Gate	Definition
Functional	The feature works on realistic seed data and handles empty, loading, success, and error states.
Technical	API contracts are typed, inputs are validated, slow queries are indexed, and state is persisted where expected.
Testing	Unit and integration tests cover happy path, edge cases, and at least one failure path.
UX	The feature is understandable without developer explanation and fits the core student decision workflow.
Docs	README or docs explain the feature, setup changes, limitations, and validation commands.

4. Final Product Surface and UX System
4.1 Final site map
Route	Screen	Purpose
/	Landing page	Explains value proposition and routes users to onboarding or search.
/onboarding	Preference quiz	Captures intended major, location, cost, career, culture, and admissions preferences.
/search	Discovery/search	Filterable and semantic school search with saved schools and compare tray.
/schools/[id]	School profile	Detailed school page with fit score, attributes, tradeoffs, and similar schools.
/compare	Comparison workspace	Side-by-side comparison for 2-5 schools with highlighted tradeoffs.
/dashboard	My schools	Saved schools, application statuses, finalist lists, notes, and ranking snapshots.
/decision	Acceptance decision mode	Post-acceptance workflow using aid offers, personal notes, and weighted tradeoffs.
/calculator	Cost/value calculator	Four-year cost, debt sensitivity, and rough outcome-adjusted value analysis.
/admin/data	Data admin optional	Data health, ingestion status, duplicate flags, and freshness checks.

4.2 Landing page requirements
•	Hero: “Find the college that actually fits you.”
•	Primary CTA: “Build my shortlist.” Secondary CTA: “Explore schools.”
•	Show one recommendation card with fit score, reasons, and tradeoffs.
•	Show one comparison preview with cost, outcomes, and campus fit.
•	Include brief trust copy: data-driven, transparent scoring, not admissions or financial advice.
•	Include footer links: GitHub, methodology, data sources, privacy note, limitations.
4.3 Onboarding quiz details
Stage	Name	Fields / behavior
Step 1	Academic goals	Intended major, backup major, flexibility, research interest, class-size preference.
Step 2	Cost constraints	Max annual cost, aid importance, debt comfort, in-state/out-of-state context.
Step 3	Career priorities	Industry interest, internships, alumni network, outcomes importance, job hub proximity.
Step 4	Campus preferences	Size, setting, weather, sports, Greek life, culture, distance from home.
Step 5	Admissions strategy	Reach/target/likely mix, selectivity tolerance, application workload.
Step 6	Weight tuning	Sliders for academic, cost, career, location, campus, prestige, admissions realism.
Output	Initial ranking	Top schools, explanations, tradeoffs, confidence level, missing-preference prompts.

4.4 Search and discovery page
•	Left filter sidebar: geography, type, size, major, acceptance rate, net price, graduation rate, setting, outcomes, culture tags.
•	Top search bar: keyword and natural-language semantic mode.
•	Result cards: school name, location, acceptance rate, net price, enrollment, top matched major, fit score, two reasons, one tradeoff.
•	Sort options: best fit, lowest net price, strongest outcomes, highest graduation rate, admissions realism, recently viewed.
•	Compare tray: user can select 2-5 schools and jump to comparison workspace.
•	Empty state: suggests loosening filters and shows which filter is most restrictive.
4.5 School profile page
•	Header: name, location, type, size, setting, saved/compare actions.
•	Fit summary: overall score, category scores, confidence label, top reasons, key risks.
•	Academics: major availability, related programs, student-faculty ratio, graduation/retention rate.
•	Cost: tuition, estimated net price, aid indicators, four-year directional estimate.
•	Outcomes: median earnings, graduation rate, debt indicators, career/outcome tags.
•	Campus life: setting, housing, sports, Greek life, diversity, weather, cultural fit tags.
•	Similar schools: “like this but cheaper,” “like this but less selective,” and “like this but smaller.”
4.6 Comparison workspace
Module	Required behavior
Top summary	Best overall fit, best value, strongest career outcome, biggest risk.
Metrics table	Cost, net price, graduation rate, median earnings, acceptance rate, size, setting, major fit.
Category winners	Highlight which school wins on academic fit, cost fit, career fit, campus fit.
Tradeoff narrative	Plain-English explanation of what the student gains and gives up.
Sensitivity control	Allow weight sliders to update comparison order.
Export/share	Generate clean report for parent/counselor conversation.

4.7 UX style guide
•	Visual tone: polished, calm, data-forward, student-friendly. Avoid childish college-themed graphics.
•	Layout inspiration: modern SaaS decision dashboard, not a government data portal.
•	Cards should be information-dense but readable, with clear hierarchy and simple badges.
•	Use color only to clarify categories and risk levels. Do not make rankings feel gamified or manipulative.
•	Every important screen must have loading, empty, error, and partially-complete states.
•	The product should feel useful on desktop first; mobile responsiveness is important but secondary for portfolio demo.
5. Technical Stack and Architecture
5.1 Recommended stack
Layer	Tooling	Rationale
Frontend	Next.js App Router + TypeScript	Strong recruiter-recognized full-stack signal; supports route organization, server/client components, and polished React UI.
Styling/UI	Tailwind CSS + shadcn/ui or equivalent	Fast polished UI, composable components, consistent design system.
Backend	FastAPI + Pydantic	Typed API contracts, Python data/ranking logic, automatic API docs, good fit with existing resume stack.
Database	PostgreSQL	Relational core for college data, user data, filters, comparisons, and analytics.
Vector search	pgvector	Semantic school matching while keeping vectors in the primary database.
Cache	Redis	Cache-aside for repeated search, school profile, and ranking queries.
Cloud	AWS	Use RDS, ElastiCache, S3/CloudFront, App Runner/ECS, CloudWatch, and Secrets Manager as appropriate.
Testing	pytest, Playwright, Vitest/React Testing Library	Covers backend logic, API integration, and critical user flows.
CI/CD	GitHub Actions	Run lint, type check, tests, migrations, build, and deployment checks.
Docs	README, architecture docs, API contract, scoring methodology, task tracker	Makes the repo legible to recruiters and LLM agents.

5.2 Architecture overview
The architecture should remain deliberately simple: a Next.js frontend calls a FastAPI backend; FastAPI owns search, ranking, comparison, preferences, and cost/value logic; PostgreSQL stores canonical data; pgvector supports semantic retrieval; Redis caches repeated read-heavy queries; AWS hosts production services.
•	Frontend never directly queries PostgreSQL.
•	Backend exposes typed REST endpoints with stable request/response schemas.
•	Ranking and scoring are service-layer modules with tests and version identifiers.
•	Data ingestion is separated from user-facing APIs.
•	Redis cache keys include versioning so ranking formula changes do not return stale scores.
5.3 Suggested repository structure
college-exploration-platform/
  apps/
    web/                 # Next.js frontend
    api/                 # FastAPI backend
  packages/
    shared-types/        # Optional generated or shared API types
  data/
    raw/                 # Raw source snapshots, not committed if too large
    processed/           # Cleaned local dev fixtures
    seed/                # Small deterministic seed dataset
  docs/
    architecture.md
    api-contract.md
    scoring-methodology.md
    data-dictionary.md
    deployment.md
    screenshots.md
  infra/
    docker/
    aws/
  tests/
    e2e/
  README.md
  AGENTS.md
  tasks.md
5.4 Backend service modules
Service	Responsibilities
Search service	Structured filters, pagination, sorting, query normalization, filter counts.
Ranking service	Weighted scoring, category scores, ranking version, explanation features.
Semantic service	Embedding lookup, vector similarity, hybrid ranking boost, similar schools.
Preference service	Onboarding answers, weight profiles, default profiles, profile completeness.
Comparison service	Side-by-side metrics, category winners, tradeoff summaries.
Decision service	Acceptance mode, aid offers, decision report, unresolved questions.
Cost/value service	Four-year cost model, debt sensitivity, directional value comparisons.
Cache service	Redis key generation, TTLs, invalidation, hit/miss logging.
Analytics service	Search events, saves, comparisons, slow queries, ranking version metrics.
Data ingestion service	Raw imports, cleaning, validation, de-duplication, data quality checks.

5.5 Deployment target
•	V1 portfolio deployment may use Vercel for frontend and AWS App Runner or ECS/Fargate for FastAPI.
•	PostgreSQL should run on managed RDS in production-like deployment, with local Docker Compose for development.
•	Redis should run locally via Docker and production-like through ElastiCache or a managed Redis provider.
•	Static public assets and generated reports can be stored on S3 with CloudFront if V3 requires it.
•	Secrets should never be committed; use local .env examples and cloud secret management.
6. Data Model and Data Pipeline
6.1 Recommended data sources
Use public institutional datasets as the source of truth, then supplement with derived tags and curated fields. Prioritize reliability over novelty. The platform should preserve source names, source years, and data freshness in the database and documentation.
Source type	Use	Notes
College Scorecard	Institution/program costs, graduation, admissions, debt, earnings, and outcome-oriented fields.	Best for outcome and cost/value data.
IPEDS / NCES	Institution metadata, enrollment, completion, financial aid, institutional characteristics.	Best for canonical school records and institutional details.
Curated derived fields	Weather bands, culture tags, major families, job hub proximity, region grouping.	Must be clearly labeled as derived, not official.

6.2 Core database entities
Entity	Purpose	Representative fields
schools	Canonical institution profile.	id, unitid, name, city, state, region, type, setting, enrollment, latitude, longitude.
school_academics	Academic metrics.	school_id, majors, popular_majors, graduation_rate, retention_rate, student_faculty_ratio.
school_costs	Cost and aid metrics.	school_id, tuition_in_state, tuition_out_state, net_price, average_aid, debt_median.
school_outcomes	Career/outcome metrics.	school_id, median_earnings, completion_rate, repayment_rate, outcome_percentiles.
school_campus_life	Lifestyle attributes.	school_id, sports, greek_life, housing, weather_band, diversity_metrics, culture_tags.
school_embeddings	Vector search.	school_id, embedding_type, embedding_model, vector, text_snapshot_hash.
users	Account identity.	id, email, created_at, auth_provider, privacy_flags.
user_preferences	Onboarding profile.	user_id, intended_major, weights_json, constraints_json, completeness_score.
saved_schools	Student lists.	user_id, school_id, list_type, status, notes, created_at.
comparisons	Saved comparison sessions.	id, user_id, school_ids, weights_snapshot, created_at.
acceptance_offers	Decision mode inputs.	user_id, school_id, status, aid_offer, scholarship, estimated_cost, notes.
ranking_results	Optional logged ranking outputs.	user_id, school_id, rank, scores_json, ranking_version, created_at.
events	Analytics.	user_id, event_type, payload_json, ranking_version, timestamp.

6.3 Data pipeline stages
8.	Raw snapshot import: store original data files or API snapshots with source date and schema version.
9.	Normalize identifiers: standardize UNITID, school names, city/state, institution type, and program taxonomy.
10.	Clean metrics: convert percentages, handle suppressed/missing values, standardize numeric scales.
11.	Derive attributes: create region, weather band, major families, selectivity tier, cost tier, outcome tier, and job hub proximity.
12.	Generate searchable text: combine official description, program list, location, derived tags, and outcome summaries.
13.	Generate embeddings: embed school search documents and store vector with model/version metadata.
14.	Validate data: enforce required fields, type ranges, duplicate checks, referential integrity, and source freshness checks.
15.	Seed dev database: create deterministic seed data for tests and demos.
16.	Document data dictionary: explain each field, source, transformation, missing-value policy, and limitation.
6.4 Missing data policy
•	Never treat missing data as zero unless zero is semantically correct.
•	For ranking, missing data should lower confidence more than it lowers the score.
•	Show “data unavailable” in UI rather than hiding important missing fields.
•	Keep confidence score separate from fit score.
•	Log which fields contributed to each recommendation explanation.
7. Ranking, Search, and Decision Logic
7.1 Ranking engine principles
•	Deterministic first: the same user profile and same ranking version should produce the same result.
•	Explainable: category scores and reason codes should be available for every ranked school.
•	Adjustable: users can change weights and immediately see ranking movement.
•	Versioned: every scoring formula should have a ranking_version identifier.
•	Testable: scorer tests should cover boundary cases, missing data, and stable ordering.
7.2 Scoring layers
Layer	Purpose	Examples
Layer 1: hard constraints	Remove schools that violate non-negotiables.	No intended major, wrong region if region locked, cost above hard maximum.
Layer 2: normalized category scores	Convert school attributes into 0-100 category scores.	Academic fit, cost fit, career fit, location fit, campus fit, admissions realism.
Layer 3: weighted aggregation	Combine category scores using user preference weights.	Cost-sensitive users see affordable schools move up.
Layer 4: semantic boost	Add bounded score adjustment from pgvector similarity.	“Schools like Berkeley but smaller.”
Layer 5: confidence and explanation	Show data completeness and reason codes.	High fit but low confidence if key data missing.

7.3 Default category weights
Category	Default weight	Inputs
Academic fit	25%	Major availability, program breadth, graduation/retention, academic environment.
Cost fit	20%	Net price, aid, user max cost, debt sensitivity.
Career fit	20%	Median earnings, job hub proximity, internship/career tags.
Campus/lifestyle fit	15%	Size, setting, sports, Greek life, weather, culture tags.
Admissions realism	10%	Selectivity relative to user strategy and desired reach/target/likely balance.
Location fit	10%	Region, distance, urban/suburban/rural, proximity preferences.

7.4 Explanation engine
Explanations should be generated from reason codes, not free-form hallucination. Each school should return top positive reasons and top tradeoffs based on the largest category contributions and penalties.
Type	Reason code	UI explanation template
Positive reason	academic_major_match	Strong match for your intended major and related academic interests.
Positive reason	career_outcome_high	Strong career/outcome indicators relative to your priorities.
Positive reason	location_match	Matches your preferred region and campus setting.
Tradeoff	cost_above_preference	Estimated cost is above your stated comfort range.
Tradeoff	selectivity_high	Admissions selectivity makes this closer to a reach school.
Tradeoff	size_mismatch	Campus size differs from your stated preference.

7.5 Semantic search behavior
•	Support natural-language searches such as “affordable data science schools near cities” or “schools like UCLA but smaller.”
•	Use embeddings to retrieve candidate schools, then re-rank using structured fit logic.
•	Always show why semantic results matched: major, location, setting, cost, or culture tags.
•	Do not let semantic similarity override hard constraints unless the user explicitly loosens filters.
•	Cache repeated semantic queries with normalized query text and ranking version in the cache key.
7.6 Decision mode logic
•	Decision mode is only for schools the user marks as accepted or finalist.
•	Inputs include aid offer, scholarship, expected yearly cost, visit notes, parent priority, student priority, and unresolved questions.
•	Outputs include best overall fit, best value, strongest career upside, lowest risk, and biggest unresolved decision factor.
•	The system should separate “best fit” from “best value” instead of forcing one answer.
•	The final report should be shareable and written in clear parent/counselor-friendly language.
8. V1 Roadmap: Production-Quality MVP
V1 goal: Build a credible full-stack platform with real search, school profiles, onboarding, deterministic ranking, saved schools, comparison, caching, deployment, and documentation. V1 should be enough to justify the current resume bullets.
V1.1 Repo foundation and documentation
•	Initialize monorepo structure with apps/web, apps/api, docs, data, infra, and tests.
•	Add README with project thesis, architecture placeholder, setup instructions, and roadmap.
•	Add AGENTS.md with coding standards, validation commands, documentation requirements, and LLM guardrails.
•	Add tasks.md with V1/V2/V3 task tracker.
•	Set up GitHub Actions skeleton for frontend lint/build and backend tests.
Acceptance gate: Repo builds locally; docs explain how to run web, API, database, and tests.
V1.2 Database schema and seed data
•	Create PostgreSQL schema for schools, academics, costs, outcomes, campus life, preferences, saved schools, comparisons, and events.
•	Add migrations and local Docker Compose for PostgreSQL.
•	Create deterministic seed dataset with at least 50 schools for local development and tests.
•	Add indexes for common filters: state, region, type, setting, enrollment, tuition, net price, acceptance rate, graduation rate.
•	Document schema and field meanings in docs/data-dictionary.md.
Acceptance gate: Seeded database supports search/profile API tests and documented schema.
V1.3 FastAPI foundation
•	Set up FastAPI app with health check, settings, database connection, error handling, and logging.
•	Define Pydantic request/response models for schools, search, profiles, preferences, rankings, saves, and comparisons.
•	Add repository layer so SQL is isolated from route handlers.
•	Add API documentation in docs/api-contract.md.
•	Add backend test framework with database fixtures.
Acceptance gate: API starts cleanly, health endpoint works, typed contracts exist, and tests run.
V1.4 Structured search API
•	Implement GET /schools/search with filters, sorting, pagination, and result counts.
•	Use parameterized SQL and validate all filter inputs.
•	Return school cards with key metrics and no unnecessary full-profile data.
•	Add slow-query logging and query plan notes for common filters.
•	Add tests for filters, pagination, invalid inputs, empty states, and sort order.
Acceptance gate: Search endpoint returns stable paginated results and handles realistic filter combinations.
V1.5 School profile API
•	Implement GET /schools/{id} with canonical details, academics, cost, outcomes, campus-life fields, and similar placeholder logic.
•	Return data freshness/source metadata when available.
•	Handle missing data explicitly instead of returning misleading zeros.
•	Add tests for complete profile, missing optional fields, and not-found behavior.
•	Document school profile response.
Acceptance gate: School profiles are complete enough to power detailed frontend pages.
V1.6 Next.js frontend foundation
•	Set up Next.js App Router with TypeScript, styling system, route layout, error boundaries, loading states, and environment configuration.
•	Create shared UI components: card, badge, button, filter panel, metric row, score pill, empty state, skeleton.
•	Add landing page with CTA and product thesis.
•	Add API client module with typed fetch wrappers.
•	Add frontend lint/build validation.
Acceptance gate: Frontend builds, landing page renders, and component system is ready for product pages.
V1.7 Search UI
•	Build search page with filter sidebar, result cards, sort dropdown, active filter chips, pagination, and empty states.
•	Debounce search inputs and keep filter state in URL parameters.
•	Add save and compare controls to cards, even if saved data is local/session-backed initially.
•	Add loading skeletons and API error display.
•	Add Playwright smoke test for search flow.
Acceptance gate: User can search, filter, sort, and inspect result cards through the UI.
V1.8 Onboarding and preference profile
•	Build preference quiz with intended major, cost, career, location, campus, admissions, and weight sliders.
•	Persist preference profile locally or through backend user/session model depending on auth readiness.
•	Add profile completeness score and default weights.
•	Connect onboarding output to ranked search results.
•	Document preference schema.
Acceptance gate: User can complete onboarding and receive a preference object used by ranking.
V1.9 Deterministic ranking engine
•	Implement category scoring for academic fit, cost fit, career fit, location fit, campus fit, and admissions realism.
•	Implement weighted aggregation and ranking_version.
•	Return category scores, confidence, top reasons, and tradeoffs for each ranked school.
•	Add unit tests for scoring boundaries, missing data, hard constraints, and stable ordering.
•	Document scoring methodology in docs/scoring-methodology.md.
Acceptance gate: Ranked results are explainable, deterministic, tested, and visible in search cards.
V1.10 School profile frontend
•	Build school detail page with fit summary, reasons, tradeoffs, academics, cost, outcomes, campus life, and actions.
•	Show missing data honestly and use confidence labels.
•	Add related/similar placeholder section for V2 expansion.
•	Add shareable school URL and basic metadata.
•	Add frontend smoke test for profile page.
Acceptance gate: School pages are polished enough for screenshots and recruiter demo.
V1.11 Saved schools and comparison MVP
•	Implement saved schools list with statuses: interested, applying, accepted, finalist, removed.
•	Implement compare tray and comparison page for 2-5 schools.
•	Show side-by-side metrics and category winners.
•	Persist saved schools and comparisons if auth exists; otherwise use local/session storage for V1 demo.
•	Add tests for comparison calculations and UI flow.
Acceptance gate: User can save schools and compare finalists side by side.
V1.12 Redis cache-aside
•	Add Redis connection and cache service abstraction.
•	Cache repeated search queries, profile responses, and ranking results with TTLs.
•	Version cache keys by schema/ranking version.
•	Add cache hit/miss logging and tests using fake Redis or integration Redis container.
•	Document cache policy and invalidation logic.
Acceptance gate: Repeated queries reduce database reads and cache behavior is measurable.
V1.13 Deployment and README polish
•	Deploy frontend and backend with production-like environment variables.
•	Create architecture diagram and local/dev/prod setup instructions.
•	Add screenshots/GIF checklist: onboarding, search, profile, compare, ranking explanations.
•	Run basic load test or benchmark for search before/after indexes/cache.
•	Finalize README with performance metrics and limitations.
Acceptance gate: The project is publicly demoable, documented, and aligned with resume bullets.
9. V2 Roadmap: Recommendation and Decision Intelligence
V2 goal: Make the product distinctive by adding semantic search, similar schools, acceptance decision mode, cost/value modeling, sensitivity analysis, and shareable reports. V2 turns the project from a search app into a decision engine.
V2.1 Data ingestion pipeline
•	Build repeatable import pipeline for public college data snapshots.
•	Add transformation stages for normalization, missing-value handling, derived attributes, and data quality checks.
•	Add CLI commands for import, validate, seed, and refresh.
•	Add source-year and data-version metadata to relevant tables.
•	Document data sources, transformations, limitations, and refresh process.
Acceptance gate: A reviewer can see how raw data becomes product-ready school records.
V2.2 pgvector semantic search
•	Create school search documents from structured fields and curated descriptive tags.
•	Generate embeddings with versioned model metadata.
•	Add pgvector index and semantic lookup endpoint.
•	Implement hybrid retrieval: vector candidates plus structured re-ranking.
•	Add tests for deterministic fallback when embeddings are missing.
Acceptance gate: Users can search natural-language preferences and receive explainable school matches.
V2.3 Similar-school discovery
•	Implement “similar to this school” recommendations using vector similarity and structured constraints.
•	Add variants: cheaper, less selective, smaller, stronger outcomes, closer to home.
•	Display similar schools on profile pages with reason tags.
•	Cache similar-school queries.
•	Add tests for variant constraints.
Acceptance gate: School profiles become discovery launchpads, not dead-end pages.
V2.4 Acceptance decision mode
•	Add accepted/finalist school workflow.
•	Allow users to enter aid offers, scholarships, estimated yearly cost, visit notes, and unresolved questions.
•	Rank accepted schools by fit, value, career upside, and risk.
•	Create decision summary with best fit, best value, lowest risk, and biggest unresolved factor.
•	Add clear disclaimer that this is decision support, not financial advice.
Acceptance gate: Users can compare actual acceptances and generate a practical decision summary.
V2.5 Cost/value calculator
•	Build calculator for estimated four-year cost, scholarship impact, loan amount, and basic repayment sensitivity.
•	Compare schools by cost gap and outcome-adjusted directional value.
•	Show uncertainty and missing-data warnings.
•	Add charts or visual summaries for cost breakdown.
•	Add unit tests for calculation scenarios.
Acceptance gate: The platform supports rational financial comparison without overclaiming.
V2.6 Sensitivity analysis
•	Add sliders for cost, career, academic, campus, location, prestige, and admissions realism.
•	Show ranking movement as weights change.
•	Identify robust top choices that stay high across scenarios.
•	Identify volatile choices that depend on one variable.
•	Add tests for ranking stability and movement explanations.
Acceptance gate: Users understand which priorities actually drive their recommendations.
V2.7 Shareable decision report
•	Generate a clean report from comparison or decision mode.
•	Include top recommendation, ranking table, category scores, cost comparison, tradeoffs, unresolved questions, and methodology note.
•	Support shareable link or export format depending on implementation scope.
•	Add parent/counselor-friendly language.
•	Add privacy controls so reports do not expose sensitive user data unintentionally.
Acceptance gate: The product produces a polished artifact that proves decision-support value.
V2.8 Analytics and ranking evaluation
•	Log searches, saves, compares, profile views, ranking versions, and weight changes.
•	Build simple analytics queries: most-used filters, save rate by rank, compare rate by category.
•	Add offline ranking evaluation: do saved schools correlate with high fit scores?
•	Document known biases and limitations of the evaluation.
•	Add basic admin dashboard or docs report.
Acceptance gate: The project shows product/data feedback loops, not just one-way recommendations.
10. V3 Roadmap: Production Hardening and Portfolio Polish
V3 goal: Make the project look and feel like a senior student portfolio piece: authenticated user workspace, observability, load testing, robust CI/CD, security review, admin tooling, and a polished demo story.
V3.1 Authentication and account persistence
•	Add login/signup using a reputable auth provider or framework-compatible auth solution.
•	Persist preferences, saved schools, comparisons, notes, decision reports, and acceptance offers by user.
•	Add authorization checks on all user-owned resources.
•	Add account deletion or data export basics if feasible.
•	Update privacy documentation.
Acceptance gate: Users can return to their decision workspace and data access is scoped correctly.
V3.2 Observability and performance dashboard
•	Add structured logging for API latency, slow queries, cache hit/miss, error rate, and ranking version.
•	Create internal dashboard or documented queries for p50/p95/p99 latency and cache performance.
•	Add endpoint-level metrics and request IDs.
•	Add alerting or at least documented thresholds.
•	Update README with measured performance results.
Acceptance gate: The project demonstrates production operations literacy.
V3.3 Load testing and query optimization
•	Create load-test scenarios for search, profile, ranking, semantic search, and comparison.
•	Benchmark before/after indexes and Redis caching.
•	Document query plans for at least three important queries.
•	Add regression thresholds for unacceptable latency if feasible.
•	Keep metrics honest and reproducible.
Acceptance gate: Performance claims are backed by reproducible measurements.
V3.4 Admin data quality console
•	Build internal admin view for data import status, missing field rates, duplicate schools, stale embeddings, and source freshness.
•	Add data validation report after ingestion.
•	Allow safe re-run of import/embedding jobs in local/dev environment.
•	Display data quality warnings before publishing new snapshot.
•	Document operational workflow.
Acceptance gate: Data pipeline quality is visible and maintainable.
V3.5 Security and privacy hardening
•	Add rate limiting to expensive endpoints.
•	Review input validation, SQL parameterization, CORS, headers, secret handling, and logging of sensitive fields.
•	Add dependency audit to CI.
•	Add privacy-safe analytics rules.
•	Document threat model and mitigations.
Acceptance gate: The app avoids common portfolio-project security weaknesses.
V3.6 End-to-end test suite
•	Add Playwright tests for onboarding -> ranked search -> profile -> compare -> decision report.
•	Add backend integration tests with seeded database and Redis.
•	Add scorer snapshot tests for stable ranking outputs.
•	Add frontend component tests for core cards and comparison modules.
•	Run all critical tests in CI.
Acceptance gate: The core demo flow is protected from regressions.
V3.7 Portfolio/demo polish
•	Record GIFs for README: onboarding, search filters, semantic search, ranking explanations, comparison, decision mode.
•	Create a 90-second demo script for recruiters.
•	Add architecture diagram, schema diagram, and ranking methodology diagram.
•	Add “engineering highlights” section to README.
•	Add “known limitations and future work” section to sound mature and honest.
Acceptance gate: The project is easy for a recruiter to understand without running it locally.
11. API Contract Outline
11.1 Core endpoints
Method	Endpoint	Purpose	Stage
GET	/health	Service health and build metadata.	V1
GET	/schools/search	Structured search with filters, sort, pagination, optional preference profile.	V1
GET	/schools/{id}	Full school profile.	V1
POST	/preferences	Create/update onboarding preference profile.	V1
POST	/rankings	Rank schools against preference profile.	V1
POST	/saved-schools	Save or update school status.	V1
GET	/saved-schools	Fetch user saved schools/list state.	V1
POST	/comparisons	Create comparison for selected schools.	V1
GET	/comparisons/{id}	Read comparison output.	V1
POST	/semantic-search	Natural-language search with vector retrieval and structured re-ranking.	V2
GET	/schools/{id}/similar	Similar-school recommendations and variants.	V2
POST	/decision/offers	Create/update acceptance and aid offer data.	V2
POST	/decision/report	Generate decision report.	V2
POST	/cost-calculator	Calculate four-year cost and debt sensitivity.	V2
POST	/sensitivity	Return ranking movement under weight changes.	V2
GET	/admin/data-quality	Data freshness and quality summary.	V3
GET	/admin/performance	Latency/cache/query summary.	V3

11.2 Search response fields
•	school_id, name, city, state, type, setting, undergraduate_enrollment.
•	acceptance_rate, net_price, graduation_rate, median_earnings if available.
•	fit_score, confidence_score, category_scores when preference profile is present.
•	top_reasons and top_tradeoffs generated from deterministic reason codes.
•	pagination metadata: page, page_size, total_results, has_next.
•	applied_filters and ranking_version for transparency and reproducibility.
11.3 Error response standards
•	400 for invalid filters or malformed request.
•	404 for unknown school/comparison/report resources.
•	422 for valid JSON with invalid semantic content, such as impossible weight totals.
•	429 for rate-limited expensive endpoints in V3.
•	500 only for unexpected server errors; logs should include request ID.
•	Frontend should show user-friendly errors and not expose stack traces.
12. Testing, Observability, and Security Gates
12.1 Test matrix
Test type	Coverage	Stage
Ranking unit tests	Scoring formulas, weights, missing data, reason codes, stable ordering.	V1
Search API tests	Filters, sorting, pagination, invalid inputs, empty results.	V1
Profile API tests	Full data, missing data, not-found behavior.	V1
Cache tests	Cache hit/miss, TTL behavior, versioned keys, invalidation.	V1
Frontend smoke tests	Search, profile, comparison, onboarding.	V1
Semantic tests	Embedding fallback, hybrid ranking, variant constraints.	V2
Cost calculator tests	Aid, scholarship, loan sensitivity, edge cases.	V2
E2E tests	Onboarding to decision report.	V3
Security tests	Dependency audit, input validation, auth boundaries.	V3

12.2 Observability metrics
•	API latency: p50, p95, p99 by endpoint.
•	Database: slow queries, query count per request, index usage notes for common searches.
•	Cache: hit rate, miss rate, evictions, average cached payload size where feasible.
•	Ranking: ranking_version, average score distribution, confidence distribution, top reason codes.
•	Product: searches, saves, compares, report generation, onboarding completion.
•	Errors: 4xx rate, 5xx rate, validation failures, failed embedding lookups.
12.3 Security and privacy requirements
•	Parameterized SQL only; no string-concatenated SQL for user inputs.
•	Validate all request inputs with typed schemas.
•	Rate-limit expensive endpoints such as semantic search, ranking, and report generation.
•	Do not log sensitive student notes, aid details, or personal profile fields in plaintext analytics logs.
•	Use CORS narrowly in production.
•	Use environment variables and cloud secrets for credentials.
•	Add clear privacy note explaining what data is stored and why.
•	Allow users to delete or clear local decision data where feasible.
13. Resume Positioning and Demo Strategy
13.1 Final resume angle
The final resume story should emphasize full-stack scale, search infrastructure, ranking systems, and product usage. This project should be the clearest proof that the candidate can build a consumer-facing system with real backend depth.
13.2 Recommended final bullets
•	Co-founded full-stack college decision platform serving 6,000+ students with Next.js, FastAPI, PostgreSQL, Redis, and AWS.
•	Built indexed search over 5,000+ college records with parameterized SQL and B-tree indexes, reducing p95 query latency 60%.
•	Developed personalized ranking engine combining pgvector semantic retrieval with weighted scoring across 50+ academic, cost, career, and campus attributes.
•	Implemented Redis cache-aside layer for search, profile, and ranking endpoints, reducing repeated database load 50%.
•	Optional replacement after V2: Built acceptance comparison workflow ranking schools by fit, net cost, career outcomes, and user-weighted tradeoffs with explainable score breakdowns.
13.3 Demo script
17.	Start on landing page: explain the product as a college decision engine, not a directory.
18.	Complete or show preference onboarding: intended major, cost sensitivity, career goals, campus preferences.
19.	Show ranked search: filters, fit scores, top reasons, tradeoffs, and fast response.
20.	Open a school profile: category scores, missing data handling, similar schools.
21.	Compare three schools: category winners and tradeoff summary.
22.	Use sensitivity sliders or decision mode: show ranking movement and final recommendation.
23.	End with engineering: architecture diagram, Redis cache, indexed SQL, pgvector, tests, and deployment.
13.4 README screenshot/GIF checklist
•	Hero/landing page screenshot.
•	Onboarding quiz GIF.
•	Search filters and ranked cards GIF.
•	School profile screenshot with fit breakdown.
•	Comparison workspace screenshot.
•	Semantic search GIF after V2.
•	Decision report screenshot after V2.
•	Architecture diagram and performance chart.
14. Appendices
14.1 LLM prompt template for each implementation step
Use this template when delegating an individual step to Codex or another coding agent:
•	You are working in a fresh coding session. First read README.md, AGENTS.md, tasks.md, docs/architecture.md, docs/api-contract.md, and any files relevant to this step.
•	Do not assume the repo matches the spec. Inspect the current implementation before editing.
•	Implement only the requested step and keep changes small, typed, tested, and documented.
•	Run relevant validation commands. If a command fails, debug and fix it before finishing.
•	Update relevant docs and tasks.md when behavior, setup, schema, or commands change.
•	Finish with a concise summary: changed files, tests run, remaining limitations, and next recommended step.
14.2 Priority order if time is limited
24.	V1 search API and database schema.
25.	V1 polished search UI and school profiles.
26.	V1 deterministic ranking and explanations.
27.	V1 comparison workspace.
28.	V1 Redis caching and performance metrics.
29.	V2 semantic search and similar schools.
30.	V2 decision mode and cost/value calculator.
31.	V3 observability, load tests, auth, and README polish.
14.3 Engineering risks and mitigations
Risk	Why it matters	Mitigation
Scope creep	Too many college features dilute the engineering story.	Gate work by V1/V2/V3 and do not build forums, essays, or admissions prediction early.
Bad data quality	College data can be incomplete or stale.	Track source year, missingness, confidence, and data dictionary.
Black-box scoring	Users may distrust rankings.	Use reason codes, category scores, and weight controls.
Overuse of LLMs	LLM outputs can hallucinate facts.	Use deterministic data for ranking; optional LLM only for summarizing known outputs.
Weak demo surface	Infrastructure may be invisible to recruiters.	Add screenshots, GIFs, architecture diagram, and measurable performance results.
Security shortcuts	Student data and notes can be sensitive.	Use auth boundaries, validation, rate limits, and privacy-safe logs.

14.4 References consulted for stack and data-source alignment
•	Next.js App Router documentation: routing, layouts, server/client components, TypeScript setup.
•	FastAPI documentation: high-performance Python API framework based on standard type hints.
•	pgvector documentation: vector similarity search inside PostgreSQL.
•	Redis cache-aside guidance: cache repeated read queries with application-controlled cache population and TTLs.
•	College Scorecard API/data documentation: school, program, cost, admissions, debt, and outcome data.
•	NCES/IPEDS data tools: institutional data for U.S. colleges and universities.
14.5 Final project north star
Build the platform so a user can answer: “Which colleges should I seriously consider, why do they fit me, what tradeoffs am I making, and what should I do next?” If every feature supports that question, the product will stay coherent and the resume story will be strong.
