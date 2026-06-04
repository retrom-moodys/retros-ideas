// Query name: DeptGrouper
let
    // Helper: collapse whitespace to single spaces
    CollapseSpaces = (txt as text) as text =>
        let
            parts = List.Select(
                List.Transform(Text.SplitAny(txt, " \t"), each Text.Trim(_)),
                each _ <> ""
            ),
            result = Text.Combine(parts, " ")
        in
            result,

    // Helper: normalize a dept string (null-safe)
    NormalizeDept = (dept as nullable text) as text =>
        let
            // coalesce nulls and enforce text type
            dRaw = if dept = null then "" else Text.From(dept),
            d0 = Text.Trim(dRaw),
            // decode HTML entities: double-encoded, then single-encoded
            d1 = Text.Replace(d0, "&amp;amp;", "&"),
            d2 = Text.Replace(d1, "&amp;", "&"),
            // fix common typos (handle both cases)
            d3 = Text.Replace(Text.Replace(d2, "Orgination", "Origination"), "orgination", "origination"),
            // ensure spaces around '&' - use temporary marker to preserve already-spaced ampersands
            d4_temp = Text.Replace(d3, " & ", "___AMP___"),
            d4 = Text.Replace(d4_temp, "&", " & "),
            d4a = Text.Replace(d4, "___AMP___", " & "),
            // collapse multiple spaces and normalize
            d5 = CollapseSpaces(d4a),
            // standardize casing for matching
            d6 = Text.Lower(d5)
        in
            d6,

    // Optimized contains-any helper: checks if normalized text contains any keyword
    // Both norm and keywords are already lowercase, so direct comparison is safe
    ContainsAny = (norm as text, keywords as list) as logical =>
        List.AnyTrue(
            List.Transform(
                keywords,
                (kw) => Text.Contains(norm, kw)
            )
        ),

    // Exact-match helper (for short/exact department names)
    ExactMatch = (norm as text, exacts as list) as logical =>
        List.AnyTrue(List.Transform(exacts, each Text.Lower(Text.Trim(_)) = norm)),

    // Main function: maps a single department to a consolidated group
    MapDeptToGroup = (dept as nullable text) as text =>
        let
            norm = NormalizeDept(dept),

            // Keyword lists - organized by category
            investmentBankingLevFin = {
                "ib lev fin", "ib", "lev fin", "lev fin origination", "lev fin credit",
                "hybrid & high yield", "high yield", "equity financing"
            },

            gcib = {
                "gcib", "gcib energy", "gcib credit review", "gcib credit",
                "global corporate", "global corporate & investment banking"
            },

            renewableEnergy = {
                "global renewable energy", "renewable energy finance", "environmental business advisory",
                "energy infrastructure investing", "sustainable fixed income"
            },

            leasing = {
                "leasing credit", "global leasing", "global vendor finance", "global leasing capital markets",
                "international asset finance", "leasing syndications", "leasing and capital", "leasing"
            },

            creditRisk = {
                "credit review", "enterprise credit", "credit risk", "risk",
                "credit research", "credit products", "wholesale credit risk", "esg credit",
                "global markets credit", "credit research - retail & con", "credit advisory",
                "international credit review", "taxable credit research", "municipal credit",
                "fixed income research", "us credit research", "credit research - auto",
                "program credit", "commercial credit", "credit - healthcare", "hy credit research",
                "underwriting", "debt advisory",
                "municipal bond research", "global research"
            },

            capitalMarkets = {
                "dcm", "capital markets", "asia debt syndicate", "muni desk", "clo syndicate", "clo primary"
            },

            structuredFinanceCLO = {
                "structured finance", "sf origination & lending", 
                "clo structuring", "clo strategy", "deal structuring", "structured products"
            },

            specialSituations = {
                "distressed debt & special situations", "special situations group", "special assets group",
                "global credit and special situations", "entertainment industries group"
            },

            comCorpBanking = {
                "private bank", "commercial banking", "corporate banking", "business banking",
                "business capital", "business lending", "public sector banking", "global banking",
                "public capital corp", "real estate corp banking"
            },

            valuationsCIO = {
                "cio", "global valuations group"
            },

            technology = {
                "tech", "tmt", "market data", "team developer"
            },

            // Matching logic - order matters: more specific first, then general
            group =
                // Rating Advisory - check before credit risk to avoid conflicts
                if ContainsAny(norm, {"rating advisory", "ratings advisory"}) then "Rating Advisory"
                // Operations & Support - check before Operations (more specific)
                else if ContainsAny(norm, {"fiduciary platforms", "fiduciary platforms & programs"}) then "Operations & Support"
                // Operations - check as exact match or when it's the main term (not part of credit operations, etc.)
                else if norm = "operations" or (Text.Contains(norm, " operations ") or Text.EndsWith(norm, " operations") or Text.StartsWith(norm, "operations ")) then "Operations"
                // Asset Management - check before other matches
                else if ContainsAny(norm, {"asset management"}) then "Asset Management"
                // Business Information - check before other matches
                else if ContainsAny(norm, {"business information"}) then "Business Information"
                // Finance - check as exact match or standalone to avoid matching "finance" in other contexts
                else if norm = "finance" or norm = "quant finance" or (Text.Contains(norm, " finance ") or Text.EndsWith(norm, " finance") or Text.StartsWith(norm, "finance ")) then "Finance"
                // Substring matches (more general) - order by specificity
                else if ContainsAny(norm, investmentBankingLevFin) then "Investment Banking & Leveraged Finance"
                else if ContainsAny(norm, gcib) then "Global Corporate & Investment Banking (GCIB)"
                else if ContainsAny(norm, renewableEnergy) then "Renewable Energy"
                else if ContainsAny(norm, leasing) then "Leasing"
                else if ContainsAny(norm, specialSituations) then "Distressed Debt & Special Situations"
                else if ContainsAny(norm, capitalMarkets) then "Capital Markets"
                else if ContainsAny(norm, structuredFinanceCLO) then "Structured Finance & CLO"
                // Credit & Risk Management - check for credit-related terms (but not rating advisory, which was checked earlier)
                else if ContainsAny(norm, creditRisk) or norm = "credit" then "Credit & Risk Management"
                else if ContainsAny(norm, comCorpBanking) then "Commercial & Corporate Banking"
                else if ContainsAny(norm, valuationsCIO) then "Valuations & CIO"
                else if ContainsAny(norm, {"equity research", "sales"}) then "Research / Sales"
                else if ContainsAny(norm, technology) then "Technology"
                else "Other"
        in
            group
in
    MapDeptToGroup