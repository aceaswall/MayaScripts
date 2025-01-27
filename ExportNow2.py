import maya.cmds as cmds
import os


def import_selected_references():
    """Importar referências apenas nos grupos selecionados do Outliner"""
    selected_groups = cmds.ls(selection=True)
    if not selected_groups:
        cmds.warning("Nenhum grupo selecionado para importação.")
        return

    for group in selected_groups:
        try:
            if cmds.referenceQuery(group, isNodeReferenced=True):
                ref_file = cmds.referenceQuery(group, filename=True)
                cmds.file(ref_file, importReference=True)
                print(f"Referência importada: {group}")
            else:
                print(f"{group} já é um objeto local.")
        except Exception as e:
            print(f"Erro ao importar referência: {group} - {e}")

    cmds.select(selected_groups)


def bake_simulation_for_selected():
    """Aplicar Bake Simulation na hierarquia completa dos grupos selecionados"""
    selected_groups = cmds.ls(selection=True)
    if not selected_groups:
        cmds.warning("Nenhum grupo selecionado para Bake.")
        return

    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)

    cmds.select(selected_groups, hierarchy=True)
    cmds.bakeResults(
        simulation=True,
        time=(start_time, end_time),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False
    )
    print("Bake Simulation aplicado com sucesso!")

    cmds.select(selected_groups)


def apply_constraints_and_remove_controllers():
    """Aplicar constraints e remover controladores após o bake"""
    selected_groups = cmds.ls(selection=True)

    # Aplicar constraints apenas nos grupos selecionados
    constraints = cmds.listRelatives(selected_groups, allDescendents=True, type='constraint') or []

    # Bake das constraints e remoção
    if constraints:
        cmds.bakeResults(
            constraints,
            simulation=True,
            t=(cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)),
            at=['translate', 'rotate', 'scale'],
            preserveOutsideKeys=True,
            disableImplicitControl=False
        )
        cmds.delete(constraints)
        print(f"Constraints aplicadas e removidas: {constraints}")
    else:
        print("Nenhuma constraint encontrada.")

    # Seleção de controladores usando sufixos _Ctrl e _CTRL
    controllers = cmds.ls([f"{group}|*_Ctrl" for group in selected_groups], type='transform') + \
                  cmds.ls([f"{group}|*_CTRL" for group in selected_groups], type='transform')

    # Deletar os controladores encontrados
    if controllers:
        cmds.delete(controllers)
        print(f"Controladores removidos: {controllers}")
    else:
        print("Nenhum controlador encontrado para remoção.")


def delete_blendshapes_grp_from_selected():
    """Remover o grupo 'BlendShapes_Grp' dentro do 'Data_Grp' apenas nos grupos selecionados"""
    selected_groups = cmds.ls(selection=True)
    for group in selected_groups:
        blendshapes_path = f"{group}|Data_Grp|BlendShapes_Grp"
        if cmds.objExists(blendshapes_path):
            cmds.delete(blendshapes_path)
            print(f"{blendshapes_path} deletado com sucesso!")
        else:
            print(f"O grupo {blendshapes_path} não foi encontrado ou já removido.")

    cmds.select(selected_groups)


def export_combined_fbx_per_group(export_directory):
    """Exportar 'Data_Grp*' e 'Render_Grp*' de cada grupo selecionado em UM único arquivo por grupo"""
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    selected_groups = cmds.ls(selection=True)

    for group in selected_groups:
        children = cmds.listRelatives(group, children=True, fullPath=True) or []
        export_groups = [child for child in children if "Data_Grp" in child or "Render_Grp" in child]

        # Exportar os grupos juntos em um único arquivo FBX
        if export_groups:
            cmds.select(export_groups)
            export_path = os.path.join(export_directory, f"{group.replace(':', '_').replace('|', '_')}_Combined.fbx")
            try:
                cmds.file(export_path, force=True, options="v=0;", type="FBX export", exportSelected=True)
                print(f"Exportado com sucesso: {export_path}")
            except Exception as e:
                print(f"Erro ao exportar {group}: {e}")
        else:
            print(f"O grupo {group} não possui 'Data_Grp' ou 'Render_Grp'.")


def run_full_pipeline(export_directory):
    """Executar o pipeline completo no Maya para os grupos selecionados"""
    print("🚀 Iniciando o pipeline completo...")

    # Etapa 1: Importar Referências
    import_selected_references()

    # Etapa 2: Aplicar Bake Simulation
    bake_simulation_for_selected()

    # Etapa 3: Aplicar Constraints e Remover Controladores
    apply_constraints_and_remove_controllers()

    # Etapa 4: Remover o grupo BlendShapes_Grp
    delete_blendshapes_grp_from_selected()

    # Etapa 5: Exportar FBX (Data_Grp* e Render_Grp* juntos no mesmo arquivo por grupo)
    export_combined_fbx_per_group(export_directory)

    print("✅ Pipeline completo executado com sucesso!")


# ✅ Defina o caminho de exportação e execute o pipeline completo:
run_full_pipeline(r"C:\Users\u049\Documents\maya")
