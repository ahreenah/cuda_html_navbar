import os
from cudatext import *

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_html_panel.ini')

class Command:
    def add_button(self,text):
        toolbar_proc(self.tb_id, TOOLBAR_ADD_ITEM)
        count = toolbar_proc(self.tb_id, TOOLBAR_GET_COUNT)
        btn_id = toolbar_proc(self.tb_id, TOOLBAR_GET_BUTTON_HANDLE, index=count-1)
        button_proc(btn_id, BTN_SET_KIND, BTNKIND_TEXT_ICON_HORZ)
        button_proc(btn_id, BTN_SET_TEXT, text)
        def callbackf():
            try:
                self.need_action=False
                print(count-1)
                coord=self.cors[count-1]
                line=ed.get_text_line(coord[0])
                new_x=coord[1]
                while new_x>0:
                    if line[new_x]=='<':
                        break
                    new_x-=1
                new_x+=1
                ed.set_caret(new_x,coord[0])
            finally:
                pass
        button_proc(btn_id,BTN_SET_KIND,BTNKIND_TEXT_ONLY)
        button_proc(btn_id, BTN_SET_DATA1, callbackf)
        toolbar_proc(self.tb_id, TOOLBAR_UPDATE)
    
    def set_buttons(self,buttons):
        toolbar_proc(self.tb_id,TOOLBAR_DELETE_ALL)
        j=0
        for i in buttons:
            self.add_button(i)
            j+=1
    
    def parse_html(self,text):
        ignore_list=['meta','br','hr']
        strs=[]
        snum=0
        for s in text.split('\n'):
            flag=0
            cs=''
            colnum=0
            for i in s:
                if i=='<':
                    flag=1
                elif i=='>':
                    flag=0
                    cs=cs.split(' ')[0]
                    if not cs in ignore_list and not cs[0]=='!':
                        strs.append(cs)
                        self.cors.append([snum,colnum])
                    cs=''
                    # ещё код
                elif flag==1:
                    cs+=i
                colnum+=1
            i=0
            while i<len(strs):
                if strs[i][0]=='/':
                    tag=strs[i][1:]
                    j=i
                    while j>=0:
                        j-=1
                        if strs[j]==tag:
                            break
                    if j>=0:
                        while j<=i:
                            i-=1
                            strs.pop(j)
                            self.cors.pop(j)
                i+=1
            print('RESULT '+str(strs))
            self.set_buttons(strs)
            self.strs=strs
            snum+=1
            print(self.cors)
    
    def __init__(self):
        lexerstring=ini_read(fn_config, 'op', 'lexers', 'HTML,HTML Diafan')
        print('LEXER LIST '+fn_config+' '+lexerstring)
        self.lexer_list=lexerstring.split(',')
        
        self.cors=[]
        self.form=dlg_proc(ed.get_prop(PROP_HANDLE_SELF),DLG_CREATE)   
        self.need_action=True
        theme=app_proc(PROC_THEME_UI_DATA_GET,'')
        bg_color=0
        for i in theme:
            if i['name']=='EdTextBg':
                bg_color=i['color']
                break
        if not bg_color:
            bg_color=333333;
        dlg_proc(self.form, DLG_PROP_SET, prop={                       
          'h':25,
          'color':bg_color,
        })                                              
        toolbar = dlg_proc(self.form, DLG_CTL_ADD, 'toolbar')
        toolbar_proc(toolbar,TOOLBAR_THEME)
        dlg_proc(self.form, DLG_CTL_PROP_SET, index=toolbar, prop={
          'name': 'tb',
          'x': 0,
          'y': 0,
          'w': 20,
          'h': 40,
          'align': ALIGN_TOP,
          #'color': 0x80B080,
        }) 
        
        self.tb_id = dlg_proc(self.form, DLG_CTL_HANDLE, index=toolbar)
        print('ID: '+str(self.tb_id))             
        self.set_buttons(['a','b','b','c'])
        dlg_proc(self.form,DLG_DOCK, index=0, prop='T')                                 
        dlg_proc(self.form,DLG_SHOW_NONMODAL)
        #dlg_proc(self.form,TREE_THEME)
        toolbar_proc(toolbar,TOOLBAR_THEME)                   
        pass 
        
    def config(self):
        file_open(fn_config)
    
    def on_open(self, name):
        print('opened file')
        if ed.get_prop(PROP_LEXER_FILE,'') in self.lexer_list:
            dlg_proc(self.form, DLG_PROP_SET, prop={                       
              'h':25,
            })
        else:
            dlg_proc(self.form, DLG_PROP_SET, prop={                       
              'h':0,
            })
            
    def on_lexer(self,ed_self):
        print('changed tab '+ed.get_prop(PROP_LEXER_FILE,''))
        if ed.get_prop(PROP_LEXER_FILE,'') in self.lexer_list:
            dlg_proc(self.form, DLG_PROP_SET, prop={                       
              'h':25,
            })
        else:
            print('hiding')
            dlg_proc(self.form, DLG_PROP_SET, prop={                       
              'h':0,
            })
        
    
    def on_tab_change(self,ed_self):
        self.on_lexer(ed_self)
    
    def on_caret(self, ed_self):
        if self.need_action:
            self.cors=[]
            self.parse_html(ed_self.get_text_substr(0,0,ed_self.get_carets()[0][0],ed_self.get_carets()[0][1]))
        self.need_action=True
        
    def on_change_slow(self, ed_self):
        print('change slow')
