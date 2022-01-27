allRowFromCsv = get_excel_rows(folderProject, actionName)
save_excel_row(allRowFromCsv, folderProject, actionName, labels, parameters, analysisId, moleculeId)
# allRowFromCsv = pd.read_csv(folderProject + '/' + actionName + '.csv')

# actionRow = pd.DataFrame(actionRowDict, index=[analysisId])
# st.text(labels)
# st.text(actionRow.index)
# # actionRow.index = labels
# pd.concat([allPreviousAction, actionRow])[labels].to_csv(folderProject + '/wlc_fit_analysis.csv',)