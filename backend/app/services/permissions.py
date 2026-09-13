"""Centralized permission checks for disease preset and intervention actions.

Kept as standalone functions (rather than inline route checks) so a future
change like "grant this one epidemiologist builtin-edit rights" only touches
the function body here, not every call site.
"""

from app.models.disease_preset import DiseasePreset
from app.models.intervention import InterventionPackage, InterventionType
from app.models.user import User, UserRole


def can_create_presets(user: User) -> bool:
    """Whether this user may create new disease presets from scratch.

    Currently: admins and epidemiologists with admin privileges only.
    """
    return user.role == UserRole.admin or (user.role == UserRole.epidemiologist and user.has_admin_privileges)


def can_edit_builtin_presets(user: User) -> bool:
    """Whether this user may directly edit built-in (is_builtin=True) presets.

    Currently: admins and epidemiologists with admin privileges only.
    Extend this function (e.g. a per-user grant lookup) rather than changing
    its call sites if that ever needs to loosen for a specific user.
    """
    return user.role == UserRole.admin or (user.role == UserRole.epidemiologist and user.has_admin_privileges)


def can_clone_presets(user: User) -> bool:
    """Whether this user may clone presets. Everyone except Policy Makers."""
    return user.role != UserRole.policy_maker


def can_edit_custom_preset(user: User, preset: DiseasePreset) -> bool:
    """Whether this user may edit a specific *custom* preset.

    A user can edit if they created it, or if they hold builtin-edit rights
    (admins / admin-privileged epidemiologists can edit anyone's custom
    preset too).
    """
    return user.id == preset.created_by or can_edit_builtin_presets(user)


def can_edit_preset(user: User, preset: DiseasePreset) -> bool:
    """Whether this user may edit this preset, built-in or custom."""
    if preset.is_builtin:
        return can_edit_builtin_presets(user)
    return can_edit_custom_preset(user, preset)


def can_delete_preset(user: User, preset: DiseasePreset) -> bool:
    """Whether this user may delete this preset.

    Built-ins are never deletable, by anyone - scenarios elsewhere reference
    presets by id, and deleting a shared built-in would break them. Custom
    presets can be deleted by their owner or by a user with builtin-edit
    rights.
    """
    if preset.is_builtin:
        return False
    return user.id == preset.created_by or can_edit_builtin_presets(user)


def can_create_intervention_types(user: User) -> bool:
    """Whether this user may create new custom intervention types.

    Everyone can create custom types - unlike disease presets, there's no
    restriction here since a custom intervention type carries no scientific
    claim beyond its own (self-authored) default_effect_size.
    """
    return True


def can_edit_builtin_intervention_types(user: User) -> bool:
    """Whether this user may directly edit built-in intervention types.

    Currently: admins and epidemiologists with admin privileges only, same
    as [[can_edit_builtin_presets]].
    """
    return user.role == UserRole.admin or (user.role == UserRole.epidemiologist and user.has_admin_privileges)


def can_clone_intervention_types(user: User) -> bool:
    """Whether this user may clone intervention types. Everyone except Policy Makers."""
    return user.role != UserRole.policy_maker


def can_edit_custom_intervention_type(user: User, intervention_type: InterventionType) -> bool:
    return user.id == intervention_type.created_by or can_edit_builtin_intervention_types(user)


def can_edit_intervention_type(user: User, intervention_type: InterventionType) -> bool:
    if intervention_type.is_builtin:
        return can_edit_builtin_intervention_types(user)
    return can_edit_custom_intervention_type(user, intervention_type)


def can_edit_package(user: User, package: InterventionPackage) -> bool:
    """Whether this user may add/remove items on this package or delete it.

    Only the creator - intervention packages have no builtin-edit-rights
    escalation the way disease presets and intervention types do, since
    they're purely user-authored bundles, not reference data.
    """
    return user.id == package.created_by


def can_delete_package(user: User, package: InterventionPackage) -> bool:
    return user.id == package.created_by
