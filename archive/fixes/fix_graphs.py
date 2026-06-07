with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''        fig = px.line(df,x="year",y="drought",title="Indice de sécheresse (0=normal - 1=sévère)",color_discrete_sequence=["#ffd700"],template="plotly_dark")
        fig.add_hline(y=0.3,line_dash="dot",line_color="orange",annotation_text="Modéré")
        fig.add_hline(y=0.6,line_dash="dash",line_color="red",annotation_text="Critique")
        fig.update_layout(**LAYOUT); st.plotly_chart(fig,use_container_width=True)
        if df["spi"].notna().any():
            fig2 = px.bar(df,x="year",y="spi",title="Indice SPI (négatif = déficit)",color="spi",color_continuous_scale=["#ff4444","#ffffff","#4db8ff"],template="plotly_dark")
            fig2.update_layout(**LAYOUT); st.plotly_chart(fig2,use_container_width=True)'''

new = '''        st.markdown("### Comment la secheresse va evoluer a " + selected_commune + " d ici 2055")
        st.caption("La ligne monte vers le rouge = la secheresse devient plus severe. En dessous de 0.3 = normal. Au dessus de 0.6 = danger.")
        fig = px.line(df,x="year",y="drought",title="Evolution de la secheresse (0=normal, 1=severe)",color_discrete_sequence=["#ffd700"],template="plotly_dark")
        fig.add_hline(y=0.3,line_dash="dot",line_color="orange",annotation_text="Attention : commence a secher")
        fig.add_hline(y=0.6,line_dash="dash",line_color="red",annotation_text="DANGER : secheresse critique")
        fig.update_layout(**LAYOUT,xaxis_title="Annee",yaxis_title="Niveau de secheresse (0=normal, 1=severe)")
        st.plotly_chart(fig,use_container_width=True)
        if df["spi"].notna().any():
            st.markdown("### Les pluies seront-elles suffisantes ?")
            st.caption("Barres bleues = bonnes pluies. Barres rouges = manque de pluie. Plus les barres rouges sont grandes, plus c est sec.")
            fig2 = px.bar(df,x="year",y="spi",title="Deficit de pluie annee par annee (barres rouges = manque de pluie)",color="spi",color_continuous_scale=["#ff4444","#ffffff","#4db8ff"],template="plotly_dark")
            fig2.update_layout(**LAYOUT,xaxis_title="Annee",yaxis_title="Niveau de pluie (positif=abondant, negatif=deficit)")
            st.plotly_chart(fig2,use_container_width=True)'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
