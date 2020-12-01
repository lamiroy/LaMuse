from glob import glob
from os.path import basename
import argparse

import PySimpleGUI as sg
from Tools.generate_segmented_pictures import generate_images
from Tools.create_original_case_study import create_case_study
from Tools.fast_style_transfer import save_image

segmentation_suffix = "_objets"

default_image_folder = './BaseImages'
default_background_folder = None
default_painting_folder = './Paintings'
default_interpretation_folder = './Interpretations'

sg.theme('DarkAmber')

layout = [[sg.Text("Dossier d'images substituts"), sg.Input(), sg.FolderBrowse(initial_folder=".")],
          # [sg.Text('Veuillez confirmer le traitement d\'images actuelles (ne pas fermer cette fenëtre durant le traitement) : ')],
          [sg.Button("Génération de substituts")],
          [sg.Text('Dossier d\'oeuvres'), sg.Input(), sg.FolderBrowse(initial_folder=".")],
          [sg.Text('Dossier d\'images de fond : '), sg.Input(), sg.FolderBrowse(initial_folder=".")],
          [sg.Button("Créer un cas d'étude")]
          ]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="LaMuse",
                                     description='Generates reinterpretations of paintings')
    parser.add_argument("input_dir", metavar='in', type=str, nargs='?', help='input directory containing paintings to '
                                                                             'reinterpret',
                        default=default_painting_folder)
    parser.add_argument("substitute_dir", metavar='sub', type=str, nargs='?', help='directory containing painting '
                                                                             'substitute images',
                        default=default_image_folder)
    parser.add_argument("output_dir", metavar='out', type=str, nargs='?',
                        help='output directory (defaults to input_dir if non specified) for interpreted paintings')
    parser.add_argument("--demo", action='store_true', help='Run in demo mode, reducing features to bare minimum')
    parser.add_argument("--nogui", action='store_true', help='Run in no-gui mode')

    args = parser.parse_args()

    # generate_images(args.input_dir, args.output_dir if args.output_dir else args.input_dir)

    window = sg.Window('Génération d\'images', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        if event == "Génération de substituts":
            if values[0]:
                default_image_folder = values[0]
            if not args.demo:
                generate_images(default_image_folder,default_image_folder+segmentation_suffix)
            else:
                sg.popup('%s inaccessible en mode demo' % event)

        if event == "Créer un cas d'étude":
            if values[0]:
                default_image_folder = values[0]
            if values[1]:
                default_painting_folder = values[1]
            if values[2]:
                default_background_folder = values[2]
            else:
                default_background_folder = default_image_folder+'/Backgrounds'

            sg.Popup("La génération de cas d'étude a commencé, en fonction du nombre de peintures fournies ceci peut "
                     "prendre un certain temps", title="Création démarrée", non_blocking=True)

            create_case_study(default_painting_folder, default_image_folder+segmentation_suffix,
                              default_background_folder, default_interpretation_folder, 1)

            image_extensions = ["jpg", "gif", "png", "tga"]
            painting_file_list = [y for x in [glob(default_painting_folder + '/*.%s' % ext) for ext in image_extensions]
                                  for y in x]

            for painting in painting_file_list:
                interpretation_file_list = [y for x in
                                      [glob(default_interpretation_folder + '/%s*.%s' % (basename(painting), ext)) for ext in image_extensions]
                                      for y in x]
                for interpretation in interpretation_file_list:
                    save_image(interpretation, painting, interpretation)

            sg.Popup("Les résultats sont disponibles dans %s" % default_interpretation_folder, title="Cas d'études terminé")

    window.close()