from __future__ import annotations

from bpy.types import Context, SpaceView3D


class HUD:
    '''Stored HUD state.'''
    header: bool = False
    toolbar: bool = False
    sidebar: bool = False
    redo: bool = False
    overlays: bool = False
    gizmo: bool = False


def hide_hud(context: Context):
    '''Hide all HUD elements, store their previous state.'''
    space_data: SpaceView3D = context.space_data

    HUD.header = space_data.show_region_header
    HUD.toolbar = space_data.show_region_toolbar
    HUD.sidebar = space_data.show_region_ui
    HUD.redo = space_data.show_region_hud
    HUD.overlays = space_data.overlay.show_overlays
    HUD.gizmo = space_data.show_gizmo

    if HUD.header:
        space_data.show_region_header = False
    if HUD.toolbar:
        space_data.show_region_toolbar = False
    if HUD.sidebar:
        space_data.show_region_ui = False
    if HUD.redo:
        space_data.show_region_hud = False
    if HUD.overlays:
        space_data.overlay.show_overlays = False
    if HUD.gizmo:
        space_data.show_gizmo = False


def show_hud(context: Context):
    '''Show HUD elements which were previously hidden.'''
    space_data: SpaceView3D = context.space_data

    if HUD.header:
        space_data.show_region_header = True
    if HUD.toolbar:
        space_data.show_region_toolbar = True
    if HUD.sidebar:
        space_data.show_region_ui = True
    if HUD.redo:
        space_data.show_region_hud = True
    if HUD.overlays:
        space_data.overlay.show_overlays = True
    if HUD.gizmo:
        space_data.show_gizmo = True

    HUD.header = False
    HUD.toolbar = False
    HUD.sidebar = False
    HUD.redo = False
    HUD.overlays = False
    HUD.gizmo = False


def abstract(function):
    '''Mark the given function as abstract.'''
    function.abstract = True
    return function


def is_abstract(function) -> bool:
    '''Check if the given function is marked as abstract.'''
    return getattr(function, 'abstract', False)
