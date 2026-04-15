# Data Catalog

| Source | Dataset | Format | Fréquence | Clé de jointure | Licence |
|---|---|---|---|---|---|
| opendata.paris.fr | Arrondissements (contours) | GeoJSON | Stable | `c_ar` | ODbL |
| opendata.paris.fr | Logements sociaux | CSV | Annuel | `c_ar` | ODbL |
| data.gouv.fr | DVF géolocalisé | CSV | Semestriel | `code_commune` + point | Licence ouverte |
| Airparif / opendata | Qualité air (indice atmo) | JSON | Quotidien | `c_ar` (géo join) | ODbL |
| data.gouv.fr | Délits enregistrés | CSV | Annuel | `code_commune` | Licence ouverte |

## Indicateurs composites (Gold)

1. **Indice de tension locative** · `prix_m2_rolling_12m / revenu_median`
2. **Score de mixité sociale** · `% logements sociaux` normalisé par densité
3. **Qualité de vie composite** · pondération air + espaces verts + délits
4. **Dynamique immobilière** · variation % prix m² sur 5 ans

Chaque indicateur est documenté dans `pipeline/gold/indicators.py` avec sa formule, ses limites et sa source.
