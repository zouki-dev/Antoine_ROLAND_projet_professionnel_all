import streamlit as st
import os
from PIL import Image

folderAnalysis = os.path.dirname(__file__).replace("\\", "/")

def presentation(folderAnalysis=folderAnalysis):
    st.sidebar.subheader("Guide:")
    st.sidebar.markdown("Avec le menu ci-dessus, vous pouvez parcourir sur mon software d'analyse de donnée pour 'Optical tweezers'.")
    st.sidebar.markdown("Parcourez les dans l'ordre. Cela vous montrera nos raw datas, comment on les fit au prédiction du 'worm like chain model' (wlc). Enfin make_all_figure vous montrera une figure pour chaque protéine et chaque manipulation que l'on a fait avec pour le projet.")
    st.sidebar.markdown("Ce software n'ai pas fait pour présenter mais manipuler nos datas. Désolé d'avance si vous ne comprenez pas ce que vous y voyez :)")

    st.title("Antoine ROLAND")

    st.video("./presentation_Antoine/presentation.mp4")

    st.header("Ingénieur Généraliste PhD développeur scientifique")
    st.subheader("Python - Streamlit")
    st.subheader("C / C++ pour l'embarqué / C piloté Python")
    image = Image.open(folderAnalysis+"/presentation_Antoine/"+'photo_Antoine.png')
    st.image(image, width=400)


    st.title("Motivation:")
    st.markdown("Passionné par l'espace, c'est avec fascination que je regarde les progrès du domaine spatial d'aujourd'hui. Je suis maintenant persuadé que de grandes choses vont être construites dans l'espace de mon vivant et je souhaite intégrer l'industrie spatial à Toulouse pour participer à ce développement.")
    st.markdown("Aussi, j'ai beaucoup eu l'envie de commencer une start-up sur la base de l'une de mes idées. Aujourd'hui, commencer une start-up est beaucoup trop complexe est risqué. Je souhaite intégrer l'industrie spatiale pour pouvoir exposer mes idées, dans la future entreprise qui me fera confiance et m'apportera son soutien.")


    st.title("Skills : Python + Streamlit")
    st.markdown("Le site sur lequel vous êtes en ce moment est en fait une façade pour l’application Python notre analyse de données chez AMOLF. Vous pouvez parcourir cette application grâce au menu en haut à gauche pour voir ses différents modes, et parcourir avec nos datas.")
    st.markdown("J'ai réalisé ce site et mon analyse de données grâce au package Python Streamlit. C'est un outil qui permet de créer une intérface graphique (comme ce site) autour de l'analyse de donnée. Streamlit propose une approche de code minimaliste avec généralement une ligne de code par élément.")
    st.markdown("De plus, de nombreuses fonctionnalités  sont disponibles automatiquements avec un code streamlit, comme la possibilité de déployer le code sur internet et de lui associer un lien (comme ce site). Mes 4 collègues peuvent maintenant faire leur data analysis Python dans le bus sur leur téléphone !")


    st.title("Mon background")
    st.subheader("PhD student - Bio-Physique")
    st.markdown("Je suis diplômé de l'école Telecom Physique Strasbourg en tant qu'ingénieur Physique et modélisation. Aujourd'hui je fais un PhD de Bio-Physique où je mesure la dynamique du repliement des protéines en mesurant leur longueur (extension) grâce à des pinces optiques.")

    expanderClpb = st.expander("Vidéo représentant mes expériences d'optical tweezers. Réalisé par Mario Avellaneda")
    expanderClpb.video(folderAnalysis+"/science_video/ClpB_mario.mp4")

    expanderMyData = st.expander("Mes datas:")
    imageMyData = Image.open(folderAnalysis + "/presentation_Antoine/my_data.jpg")
    expanderMyData.image(imageMyData)


    st.title("Mon projet professionnel")
    st.markdown("Pour réaliser mes ambitions je souhaite rejoindre l'industrie du spatiales. Pour ce faire, je compte utiliser mes compétences Python et Streamlit pour réaliser des applications client issues de data du domaine spatial. D'autre part, je souhaite évoluer vers une position et un environnement où je pourrai proposer mes projets.")


    st.title("Mes projets de technologies spatiales")
    catapulteExpander = st.expander("Catapulte lunaire")
    catapulteExpander.markdown("Sur la lune il y a deux types d'objet: Le régolithe et des cailloux. Ne pourrait-on pas fabriquer des catapultes sur la lune pour déplacer sur de grande distance les cailloux lunaires? Les roues ne pourront jamais déplacer de grande quantité de matériaux sur la lune, alors pourquoi ne pas profiter du fait qu'il n'y ait pas d'atmosphère et de la gravité réduite pour lancer directement les cailloux vers la base lunaire?")
    spaceHoookExpander = st.expander("SpaceHook lunaire")
    spaceHoookExpander.markdown("La propulsion par éjection de carburant n'est pas la seul façon d'accélérer dans l'espace. Il est également possible de s'accrocher à un câble gigantesque (100km) en rotation sur lui même. Le mouvement de la pointe du câble est la combinaison de la vitesse du câble en orbite autour de la Terre et de la vitesse de rotation du câble. Ces deux vitesses vont tantôt s'ajouter, tantôt se soustraire. Cela permet de récupérer un deltaV de deux fois la vitesse de rotation de la pointe du câble. Pour la Lune, les matériaux actuels sont suffisamment résistants pour soutenir la rotation requise pour atterrir et décoller de la Lune à l'orbite basse lunaire.")


    st.title("Contact")
    st.subheader("Antoine ROLAND")
    st.subheader("ant.rol@hotmail.fr")
    st.subheader("5 rue d'hingettes,")
    st.subheader("62290, Noeux-les-Mines")
    st.subheader("https://www.linkedin.com/in/antoine-roland-929511150/")


    if st.checkbox("Cliquez si vous êtes intéressé par mes projets, mes compétences en tant que développeur Python, et que vous souhaitez travaillez avec moi!"):
        st.balloons()
        st.text("Toujours faire poper quelque ballons quand le script a fini de process!")
        st.title("Livre d'or")
        message = st.text_input("Leave a message !")
        autor = st.text_input("Who are you ?").replace(" ","_")
        if st.button("Save"):
            f = open(folderAnalysis+"/presentation_Antoine/livre_d_or"+"/"+autor+".txt", "w+")
            f.write(message)
            f.close()

        for file in os.listdir(folderAnalysis+"/presentation_Antoine/livre_d_or"):
            f = open(folderAnalysis+"/presentation_Antoine/livre_d_or"+"/"+file,"r")
            text = f.read()
            f.close()
            st.subheader(file[:-4])
            st.text(text)
    return

if __name__ == '__main__':
    presentation()