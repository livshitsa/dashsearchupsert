import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dbops
app = dash.Dash(__name__)
engine = dbops.getEngine()
searchResults=[] # global var to store results

def getLabelForId(id):
    ret = [item['label'] for item in searchResults if item['value'] == id]
    if len(ret):
        return ret[0]
    else:
        return None

def searchAndBuildResults(searchTerm):
    ret = dbops.searchCustomer(engine,searchTerm)
    data=[]
    for item in ret:
        val ={'value':item['customerid']}
        if item['include_exclude_flag']:
            if item['include_exclude_flag']=='i':
                val.update({'label': item['lastname'] + ' - included'})
            else:
                val.update({'label': item['lastname'] + ' - excluded'})
        else:
            val.update({'label': item['lastname'] + ' - not in grouping'})
        data.append(val)
    return data


app.layout = html.Div([
    html.A(html.Button('Refresh Page'),href='./'),
    html.Div(dcc.Input(id='input-on-submit', type='text')),
    html.Button('Search', id='search-val', n_clicks=0),
    html.Div(id='search-button-msg',
             children='Enter a value and press submit'),
    html.Div(id='search_results',children=[]),
    html.Div(id='dropdown-placeholder',children=[]),

    html.Div(id='selected-info'),
    html.Button('change to included', id='change-to-included', disabled=True),
    html.Button('change to excluded', id='change-to-excluded', disabled=True),
    html.Button('add as excluded', id='add-as-excluded', disabled=True),
    html.Button('add as icluded', id='add-as-included', disabled=True),
    html.Div(id='msg-placeholder',children=[])
])

@app.callback(
    [Output('dropdown-placeholder', 'children')],
    [Input('search-val', 'n_clicks')],
    [State('input-on-submit', 'value')],prevent_initial_call=True)
def update_button_output(n_clicks, inputvalue):
    global searchResults
    children=[]
    if n_clicks > 0:
        searchResults = searchAndBuildResults(inputvalue)
        children = dcc.Dropdown(id='cust-dropdown', options =searchResults)
    return [children]

@app.callback(
    [Output('selected-info', 'children'),
    Output('change-to-included', 'disabled'),
     Output('change-to-excluded', 'disabled'),
     Output('add-as-excluded', 'disabled'),
     Output('add-as-included', 'disabled')],
    [Input('cust-dropdown', 'value')],
    prevent_initial_call=True)
def update_selection(value):
    change_to_includedFlag = True
    change_to_excludedFlag = True 
    add_as_excludedFlag = True
    add_as_icludedFlag = True 
    label = getLabelForId(value)
    if label and ' - excluded' in label:
        change_to_includedFlag= False
    if label and ' - included' in label:
        change_to_excludedFlag= False
    if label and ' - not in grouping' in label:
        add_as_excludedFlag = False
        add_as_icludedFlag = False 
    return 'You have selected "{}-{}"'.format(label,value), change_to_includedFlag, change_to_excludedFlag,add_as_excludedFlag,add_as_icludedFlag


@app.callback(
    [Output('msg-placeholder', 'children'),
    Output('cust-dropdown', 'options')],
    [Input('change-to-included', 'n_clicks'),
    Input('change-to-excluded', 'n_clicks'),
    Input('add-as-excluded', 'n_clicks'),
    Input('add-as-included', 'n_clicks')],
    [State('cust-dropdown', 'value'),State('input-on-submit', 'value')],
    prevent_initial_call=True)
def change_to_included_button_output(included_n_clicks,excluded_n_clicks,add_excluded_clicks,add_included_clicks, selected_custId, searchTerm):
    global searchResults
    flag=''
    statement=''
    element = dash.callback_context.triggered[0]['prop_id']
    if element in ['change-to-included.n_clicks', 'add-as-included.n_clicks']:
        flag='i'
    if element in ['change-to-excluded.n_clicks','add-as-excluded.n_clicks']:
        flag='e'
    if element in ['change-to-included.n_clicks', 'change-to-excluded.n_clicks']:
        statement = dbops.buildUpdate(selected_custId,flag)
    if element in ['add-as-included.n_clicks', 'add-as-excluded.n_clicks']:
        statement = dbops.buildInsert(selected_custId,flag)
    
    exc = dbops.processDBOperation(engine,statement)
    msg=f"processing of {selected_custId} "
    if not exc:
        msg += 'successful'
        searchResults = searchAndBuildResults(searchTerm)
    else:
        msg += ' returned '+exc
    return [msg],searchResults

if __name__ == "__main__":
    app.config.suppress_callback_exceptions = True

    # app.config.update({
    #     # as the proxy server will remove the prefix
    #     'routes_pathname_prefix': '/app_direct/fileupload/',

    #     # the front-end will prefix this string to the requests
    #     # that are made to the proxy server
    #     'requests_pathname_prefix': '/app_direct/fileupload/'
    # })
    app.run_server(debug=True, host='0.0.0.0',port=8888)
