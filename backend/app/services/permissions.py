"""Centralized permission checks for disease preset actions.

Kept as standalone functions (rather than inline route checks) so a future
change like "grant this one epidemiologist builtin-edit rights" only touches
the function body here, not every call site.
"""

from app.models.disease_preset import DiseasePreset
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
