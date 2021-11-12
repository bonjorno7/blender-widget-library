from __future__ import annotations

from bpy.types import Context, SpaceView3D


class _HUD:
    '''Stored HUD state.'''
    header: bool = False
    toolbar: bool = False
    sidebar: bool = False
    redo: bool = False
    overlays: bool = False
    gizmo: bool = False


def hide_hud(
    context: Context,
    header: bool = False,
    toolbar: bool = False,
    sidebar: bool = False,
    redo: bool = False,
    overlays: bool = False,
    gizmo: bool = False,
):
    '''Hide all HUD elements, store their previous state.'''
    space_data: SpaceView3D = context.space_data

    if header:
        _HUD.header = space_data.show_region_header
    if toolbar:
        _HUD.toolbar = space_data.show_region_toolbar
    if sidebar:
        _HUD.sidebar = space_data.show_region_ui
    if redo:
        _HUD.redo = space_data.show_region_hud
    if overlays:
        _HUD.overlays = space_data.overlay.show_overlays
    if gizmo:
        _HUD.gizmo = space_data.show_gizmo

    if _HUD.header:
        space_data.show_region_header = False
    if _HUD.toolbar:
        space_data.show_region_toolbar = False
    if _HUD.sidebar:
        space_data.show_region_ui = False
    if _HUD.redo:
        space_data.show_region_hud = False
    if _HUD.overlays:
        space_data.overlay.show_overlays = False
    if _HUD.gizmo:
        space_data.show_gizmo = False


def show_hud(context: Context):
    '''Show HUD elements which were previously hidden.'''
    space_data: SpaceView3D = context.space_data

    if _HUD.header:
        space_data.show_region_header = True
    if _HUD.toolbar:
        space_data.show_region_toolbar = True
    if _HUD.sidebar:
        space_data.show_region_ui = True
    if _HUD.redo:
        space_data.show_region_hud = True
    if _HUD.overlays:
        space_data.overlay.show_overlays = True
    if _HUD.gizmo:
        space_data.show_gizmo = True

    _HUD.header = False
    _HUD.toolbar = False
    _HUD.sidebar = False
    _HUD.redo = False
    _HUD.overlays = False
    _HUD.gizmo = False


def abstract(function):
    '''Mark the given function as abstract.'''
    function.abstract = True
    return function


def is_abstract(function) -> bool:
    '''Check if the given function is marked as abstract.'''
    return getattr(function, 'abstract', False)
