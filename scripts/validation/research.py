"""Validate durable knowledge retrieval and source-grounded research."""

from __future__ import annotations

from pathlib import Path

from .shared import (
    Finding,
    is_string_list,
    load_mapping,
    relative,
    validate_fixture_contract_values,
)


REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS = {
    "authoritative-source",
    "conflicting-note",
    "missing-capability-fallback",
    "no-mutation",
    "ordinary-files-only",
    "stale-note",
}


SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT = {
    "question_framed": True,
    "decision_use_framed": True,
    "currency_requirement_framed": True,
    "question_specific_source_hierarchy": True,
    "primary_sources_preferred": True,
    "claim_scoped_evidence": True,
    "findings_separate_from_inference": True,
    "read_only_research": True,
    "copyright_boundary_preserved": True,
    "private_data_excluded": True,
    "credentials_excluded": True,
    "restricted_sources_respected": True,
    "standalone_supported": True,
}


REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS = {
    "stale-source": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "stale_source_retained": True,
        "stale_source_qualified": True,
        "current_claim_allowed": False,
    },
    "conflicting-sources": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "both_sources_retained": True,
        "disagreement_explicit": True,
        "false_consensus_created": False,
        "unresolved_uncertainty_explicit": True,
    },
    "no-primary-source": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "primary_source_available": False,
        "bounded_primary_search_attempted": True,
        "secondary_source_labelled": True,
        "confidence_reduced": True,
        "missing_evidence_explicit": True,
    },
    "read-only-output": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "output_mode": "inline",
        "durable_artifact_created": False,
        "local_knowledge_mutated": False,
        "evidence_delta_returned": True,
    },
    "durable-capture": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "durable_capture_requested": True,
        "durable_capture_authorized": True,
        "capture_convention": "project-owned-or-external-docs",
        "concise_attributed_summary": True,
        "duplicate_truth_created": False,
        "documentation_mirror_created": False,
        "automatic_capture": False,
    },
    "no-delegation-fallback": {
        **SOURCE_GROUNDED_RESEARCH_SHARED_CONTRACT,
        "delegation_available": False,
        "background_agents_required": False,
        "single_agent_completed": True,
        "evidence_standard_preserved": True,
    },
}


def validate_knowledge_retrieval_fixtures(repo: Path) -> list[Finding]:
    """Validate the portable knowledge-retrieval behavior fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "knowledge-retrieval"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/knowledge-retrieval",
                "no knowledge-retrieval fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported knowledge-retrieval fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate knowledge-retrieval fixture identifier: {identifier}",
                )
            )
        identifiers.add(identifier)

        if not isinstance(fixture.get("expected"), dict):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval fixture expected must be a mapping",
                )
            )
        if not is_string_list(
            fixture.get("prohibited_behaviors"),
            allow_empty=False,
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "knowledge-retrieval prohibited_behaviors must be "
                    "a non-empty string list",
                )
            )

        expected = fixture.get("expected")
        evidence_bundle = (
            expected.get("evidence_bundle")
            if isinstance(expected, dict)
            else None
        )
        if evidence_bundle is not None:
            required_evidence_fields = {
                "identifier",
                "relevance",
                "applicable_scope",
                "finding",
                "provenance",
                "freshness",
                "confidence",
                "uncertainty",
            }
            if (
                not isinstance(evidence_bundle, list)
                or not evidence_bundle
                or any(
                    not isinstance(entry, dict)
                    or not required_evidence_fields.issubset(entry)
                    for entry in evidence_bundle
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence entries require identifier, "
                        "relevance, applicable_scope, finding, provenance, "
                        "freshness, confidence, and uncertainty",
                    )
                )
            elif any(
                not isinstance(entry.get("freshness"), str)
                or entry["freshness"].strip().casefold()
                in {"current", "stale", "unknown"}
                for entry in evidence_bundle
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "retrieved evidence freshness requires a commit, "
                        "date, or equivalent traceable marker",
                    )
                )
        if identifier == "authoritative-source" and isinstance(expected, dict):
            search = expected.get("search")
            if (
                not isinstance(search, dict)
                or search.get("progressive") is not True
                or search.get("read_only") is not True
                or search.get("external_web") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval search must be progressive, "
                        "read-only, and exclude external web research",
                    )
                )
            ranking_factors = expected.get("ranking_factors")
            required_ranking_factors = {
                "authority",
                "relevance",
                "confidence",
                "maturity",
                "freshness",
            }
            if (
                not isinstance(ranking_factors, dict)
                or any(
                    ranking_factors.get(factor) is not True
                    for factor in required_ranking_factors
                )
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval ranking requires authority, "
                        "relevance, confidence, maturity, and freshness",
                    )
                )
            required_classifications = {
                "authoritative",
                "history",
                "observation",
                "inference",
                "brainstorming",
                "stale",
            }
            classifications = expected.get("classifications_supported")
            if (
                not is_string_list(classifications, allow_empty=False)
                or not required_classifications.issubset(classifications)
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must distinguish authoritative, "
                        "history, observation, inference, brainstorming, and "
                        "stale material",
                    )
                )
            ranked_results = expected.get("ranked_results")
            first_result = (
                ranked_results[0]
                if isinstance(ranked_results, list) and ranked_results
                else None
            )
            if (
                not isinstance(first_result, dict)
                or first_result.get("classification") != "authoritative"
                or first_result.get("freshness") != "current"
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must rank current authoritative "
                        "evidence first",
                    )
                )
        if identifier == "conflicting-note" and isinstance(expected, dict):
            conflict = expected.get("conflict")
            if (
                not isinstance(conflict, dict)
                or conflict.get("reported") is not True
                or conflict.get("silently_merged") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must report conflicts without "
                        "silently merging",
                    )
                )
            conflict_evidence = expected.get("evidence_bundle")
            current_authority = (
                conflict.get("current_authority")
                if isinstance(conflict, dict)
                else None
            )
            current_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("identifier") == current_authority
                    and entry.get("validity") == "current"
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            invalidated_entries = (
                [
                    entry
                    for entry in conflict_evidence
                    if isinstance(entry, dict)
                    and entry.get("validity") == "invalidated"
                    and entry.get("invalidated_by") == current_authority
                ]
                if isinstance(conflict_evidence, list)
                else []
            )
            if (
                not isinstance(conflict_evidence, list)
                or len(conflict_evidence) != 2
                or len(current_entries) != 1
                or len(invalidated_entries) != 1
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "resolved conflicts must preserve both evidence "
                        "entries and link the invalidated entry to current "
                        "authority",
                    )
                )
            nurture = expected.get("nurture")
            if (
                not isinstance(nurture, dict)
                or nurture.get("route_to") != "learning-capture"
                or nurture.get("performed") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval may recommend learning-capture "
                        "but cannot perform nurturing",
                    )
                )
        if identifier == "stale-note" and isinstance(expected, dict):
            if (
                expected.get("report_staleness") is not True
                or expected.get("silently_discard") is not False
                or expected.get("silently_merge") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "stale knowledge must be reported without silent "
                        "merge or discard",
                    )
                )
        if identifier == "ordinary-files-only" and isinstance(expected, dict):
            selected_path = expected.get("selected_path")
            selected_source_exists = (
                isinstance(selected_path, str)
                and (fixture_root / selected_path).is_file()
            )
            if (
                not selected_source_exists
                or expected.get("ordinary_files_sufficient") is not True
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "ordinary-file retrieval requires a real selected_path "
                        "and ordinary_files_sufficient=True",
                    )
                )
        if identifier == "missing-capability-fallback" and isinstance(
            expected,
            dict,
        ):
            fallback = expected.get("fallback")
            if (
                not isinstance(fallback, dict)
                or fallback.get("ordinary_files") is not True
                or expected.get("blocked") is not False
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "missing capabilities must fall back to ordinary "
                        "local files",
                    )
                )
            if expected.get("external_web") is not False:
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval fixtures must keep external web "
                        "research out of scope",
                    )
                )
        if identifier == "no-mutation" and isinstance(expected, dict):
            mutation_fields = {
                "filesystem_mutated",
                "index_created",
                "cache_created",
                "note_updated",
            }
            if any(
                expected.get(field) is not False
                for field in mutation_fields
            ):
                errors.append(
                    Finding(
                        fixture_label,
                        "knowledge retrieval must not mutate files, notes, "
                        "indexes, or caches",
                    )
                )

    errors.extend(
        Finding(
            "stack/fixtures/knowledge-retrieval",
            f"missing required knowledge-retrieval fixture: {identifier}",
        )
        for identifier in sorted(
            REQUIRED_KNOWLEDGE_RETRIEVAL_FIXTURE_IDENTIFIERS - identifiers
        )
    )
    return errors


def validate_source_grounded_research_fixtures(repo: Path) -> list[Finding]:
    """Validate the portable external-research behavior fixtures."""

    fixture_root = repo / "stack" / "fixtures" / "source-grounded-research"
    fixture_paths = sorted(fixture_root.glob("*.yaml"))
    if not fixture_paths:
        return [
            Finding(
                "stack/fixtures/source-grounded-research",
                "no source-grounded-research fixtures found",
            )
        ]

    errors: list[Finding] = []
    identifiers: set[str] = set()
    required_evidence_fields = {
        "identifier",
        "relevance",
        "applicable_scope",
        "finding",
        "provenance",
        "freshness",
        "confidence",
        "uncertainty",
    }

    for fixture_path in fixture_paths:
        fixture_label = relative(fixture_path, repo)
        fixture, fixture_errors = load_mapping(fixture_path, fixture_label)
        errors.extend(fixture_errors)
        if fixture is None:
            continue

        if fixture.get("schema_version") != "1.0.0":
            errors.append(
                Finding(
                    fixture_label,
                    "unsupported source-grounded-research fixture schema_version",
                )
            )

        identifier = fixture.get("identifier")
        if not isinstance(identifier, str):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research fixture identifier must be a string",
                )
            )
            continue
        if identifier in identifiers:
            errors.append(
                Finding(
                    fixture_label,
                    f"duplicate source-grounded-research fixture identifier: "
                    f"{identifier}",
                )
            )
        identifiers.add(identifier)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research fixture expected must be a mapping",
                )
            )
            continue
        if not is_string_list(fixture.get("prohibited_behaviors"), allow_empty=False):
            errors.append(
                Finding(
                    fixture_label,
                    "source-grounded-research prohibited_behaviors must be a "
                    "non-empty string list",
                )
            )

        contract = REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS.get(
            identifier
        )
        if contract is None:
            errors.append(
                Finding(
                    fixture_label,
                    f"unsupported source-grounded-research fixture: {identifier}",
                )
            )
            continue
        errors.extend(
            validate_fixture_contract_values(
                expected,
                contract,
                fixture_label,
                f"{identifier} behavior",
            )
        )

        evidence_delta = expected.get("evidence_delta")
        if (
            not isinstance(evidence_delta, list)
            or not evidence_delta
            or any(
                not isinstance(entry, dict)
                or not required_evidence_fields.issubset(entry)
                for entry in evidence_delta
            )
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "research evidence entries require identifier, relevance, "
                    "applicable_scope, finding, provenance, freshness, "
                    "confidence, and uncertainty",
                )
            )
        if isinstance(evidence_delta, list) and any(
            isinstance(entry, dict)
            and (
                not isinstance(entry.get("freshness"), str)
                or entry["freshness"].strip().casefold()
                in {"current", "stale", "unknown"}
            )
            for entry in evidence_delta
        ):
            errors.append(
                Finding(
                    fixture_label,
                    "research evidence freshness requires a publication, "
                    "version, retrieval date, or equivalent traceable marker",
                )
            )

    errors.extend(
        Finding(
            "stack/fixtures/source-grounded-research",
            f"missing required source-grounded-research fixture: {identifier}",
        )
        for identifier in sorted(
            set(REQUIRED_SOURCE_GROUNDED_RESEARCH_FIXTURE_CONTRACTS)
            - identifiers
        )
    )
    return errors
