class Product_repr(object):
    '''counter variable keep track on the number of instances,
    this allows to associate information to a specific instance''' 
    counter = 0
    def __init__(self, product, min_size = 150, max_size = 750, height = 35, overlap = 30):
        self.prod = product
        self.frag_list = product.source_fragments
        self.frag_N = product.number_of_fragments
        Product_repr.counter += 1
        
        self.fragment_height = height
        self.frag_max_size = max_size
        self.overlap_width = overlap
        
        '''min_size is the lenght reference, each fragment lenght will be
        proportional to the smaller fragment which lenght will be min_size'''
        self.proportion = min_size/len(min(self.frag_list, key =len))
        
        self.width = sum([self.normalized_size(x) for x in range(self.frag_N)]) + self.frag_N*self.overlap_width + 100
        self.height = height*12
    
    '''To avoid overly large fragment representations, max_size will be a threshold, 
    every fragment bigger than that value will be represented with lenght=max_size.
    max_size can be None, in that case, there won't be applied any threshold'''
    def normalized_size(self, frag):
        Frag_len = len(self.frag_list[frag]) * self.proportion
        if self.frag_max_size == None:
            pass
        elif Frag_len > self.frag_max_size:
            Frag_len = self.frag_max_size
        return Frag_len
    

    def _repr_javascript_(self):
        from IPython.display import display_html
        html='''<html>
                  <head></head>
                  <style>
                  .modal-body {{
                    word-wrap: break-word;
                    <!--Comment: DNA sequences will break at the box border-->
                  }}
                  </style>
                  <body>
                    <canvas id='Prod{c}'></canvas>
                    <div id="modal_body{c}"></div>
                  </body>
               </html>'''.format(c = self.counter)
        display_html(html, raw=True)
        
        return self.get_js()
    
    def get_js(self):
        begin_x = 60
        middle_y = self.fragment_height*2.5      #longitudinal axis
        delta_y = self.fragment_height*1.5       #distance to axis
        begin_y = middle_y - delta_y
        end_x = begin_x + self.normalized_size(0)
        
        # variables to be used on overlaps representation
        end_y_in = begin_y + self.fragment_height
        end_y_out = begin_y + self.fragment_height/2
        corner = self.overlap_width/2
        js = '''
        // to get the click position
        function getMousePos(canvas, event) {{
            var rect = canvas.getBoundingClientRect();
            return {{
                x: event.clientX - rect.left,
                y: event.clientY - rect.top
            }};
        }};
        
        // to check if it is inside a fragment
        function isInside(pos, rect){{
            return pos.x > rect.x && pos.x < rect.x+rect.width && pos.y < rect.y+rect.height && pos.y > rect.y
        }};
        
        var c = document.getElementById('Prod{counter}');
        var ctx = c.getContext('2d');
        ctx.canvas.width  = {Can_W};
        ctx.canvas.height = {Can_H};
        
        ctx.strokeStyle = "#f65555";
        ctx.shadowBlur=10; ctx.shadowOffsetY=5; ctx.shadowColor="grey";
        ctx.font="15px Arial"; ctx.textAlign="center";
        
        ctx.lineWidth = {C};
        ctx.lineJoin="round";
        
        // first fragment
        ctx.beginPath();
        ctx.fillStyle = "#ffff80";
        ctx.fillRect({Start}, {Begin_y}, {L}, {H});
        ctx.fillStyle = "black";
        ctx.fillText("{Name}", {Start}+({L}/2), {Begin_y}+{H}/2+5);
        
        var rect0 = {{x:{Start}, y:{Begin_y}, width:{L}, height:{H} }};    //to be passed to isInside function
        
        var modal = document.getElementById("modal_body{counter}")
        
        var empty_text = document.createTextNode('');
        
        // Features displayed on information box
        
        var fragLen = document.createElement('p');
            fragLen.appendChild(empty_text);
            fragLen.innerHTML = "<b><u>Length</u>:</b><br>{F_len}"
        var seq53 = document.createElement('p');
            seq53.appendChild(empty_text);
            seq53.innerHTML = "<br><b><u>5'-3' strand</u>:</b><br><font face='courier'>{seq}</font>";
        var seq35 = document.createElement('p');
            seq35.appendChild(empty_text);
            seq35.innerHTML = "<br><b><u>3'-5' strand</u>:</b><br><font face='courier'>{seqI}</font>";
        var description = document.createElement('p');
            description.appendChild(empty_text);
            description.innerHTML = "<br><b><u>Description</u>:</b><br>{Desc}"
        var isorf = document.createElement('p');
            isorf.appendChild(empty_text);
            isorf.innerHTML = "<br><b><u>Sequence is orf</u>:</b><br>{orf}"
        var GCcont = document.createElement('p');
            GCcont.appendChild(empty_text);
            GCcont.innerHTML = "<br><b><u>GC content (%)</u>:</b><br>{GC}"
            
        // HTML div container for features text
        // and addition of paragraphs
        
        var new0 = document.createElement('div');
            modal.appendChild(new0)
            new0.id = "mod{counter}_div0";
            new0.style = "display: none";        // text will be hidden by default

        var info_text0 = document.getElementById('mod{counter}_div0');
            info_text0.appendChild(fragLen);
            info_text0.appendChild(seq53);
            info_text0.appendChild(seq35);
            info_text0.appendChild(description);
            info_text0.appendChild(isorf);
            info_text0.appendChild(GCcont);
            
        // Function to be executed on click
        // 1 - get click position
        // 2 - Check if click is inside figure
        // 3 - create and display information box
        // 3.1 - reveal text (hidden by default)
        // 3.2 - Set text to the body of the box
        
        c.addEventListener('click', function(evt) {{
            var mousePos = getMousePos(c, evt);
            debugger;
            if (isInside(mousePos,rect0)) {{
                require(
                        ["base/js/dialog"], 
                        function(dialog) {{
                            new0.style = "display: block";
                            dialog.modal({{
                                title: '{Name}',
                                body: info_text0,
                                buttons: {{
                                    'Close': {{}}
                                }}
                            }});
                        }}
                    );
            }}
        }}, false);
        '''.format(counter = self.counter,
                   Can_W = self.width,
                   Can_H = self.height,
                   H = self.fragment_height,
                   L = self.normalized_size(0),
                   Start = begin_x,
                   Begin_y = begin_y,
                   C = corner,
                   Name = self.frag_list[0].name,
                   F_len = len(self.frag_list[0]),
                   seq = self.frag_list[0].seq.watson,
                   seqI = self.frag_list[0].seq.crick[::-1],
                   Desc = self.frag_list[0].description,
                   orf = self.frag_list[0].isorf(),
                   GC = self.frag_list[0].gc())
        
        '''to use python variables on javascript code (on string), 
        the variables are passed through format method with a key value'''
        
        
        for Frag in range(1, self.frag_N):
            start_x = end_x + self.overlap_width
            
            js= js + '''
            // overlap on previous fragment
            
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({End}+{C}/2, {Mid_y} -(Math.pow(-1,{n}-1)*{Delta})+{C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({End}, {Mid_y} -(Math.pow(-1,{n}-1)*{Delta}), {Ovr}-{C}, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {End} + {Ovr}/2, {Mid_y} -(Math.pow(-1,{n}-1)*{Delta})+{H}/2+5);
            
            ctx.shadowColor="grey";
            
            // overlap on actual fragment
            
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({Start}-({Ovr}-{C}/2), {Mid_y}-(Math.pow(-1,{n})*{Delta})+{C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({Start}-({Ovr}-{C}/2), {Mid_y}-(Math.pow(-1,{n})*{Delta}), {Ovr}-{C}/2, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {Start} - {Ovr}/2, {Mid_y} -(Math.pow(-1,{n})*{Delta})+{H}/2+5);
            
            // dashed lines connecting both overlap figures
            
            ctx.beginPath();
            ctx.lineWidth = 0.5;
            ctx.setLineDash([5, 6]);
            ctx.moveTo({Start} -{Ovr}, {y_in});
            ctx.lineTo({Start} -{Ovr}, {H}/2 + {Mid_y} -(Math.pow(-1,{n})*{Delta}));
            ctx.stroke();
            ctx.moveTo({Start}, {y_out});
            ctx.lineTo({Start}, {Mid_y} -(Math.pow(-1,{n})*({Delta}+{Par}*{H})));
            ctx.stroke();
            
            ctx.lineWidth = {C};
            ctx.setLineDash([]);
            
            // new fragment
            
            ctx.shadowColor="grey";
            ctx.beginPath();
            ctx.fillStyle = "#ffff80";
            ctx.fillRect({Start}, {Mid_y} -(Math.pow(-1,{n})*{Delta}), {L}, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{Name}", {Start} + {L}/2, {Mid_y} -(Math.pow(-1,{n})*{Delta}) +{H}/2+5);
            
            
            var rect{n} = {{x:{Start}, y:{Mid_y} -(Math.pow(-1,{n})*{Delta}), width:{L}, height:{H} }};
            
            var fragLen{n} = document.createElement('p');
            var empty_text = document.createTextNode('');
                fragLen{n}.appendChild(empty_text);
                fragLen{n}.innerHTML = "<b><u>Length</u>:</b><br>{F_len}"
            var seq53{n} = document.createElement('p');
                seq53{n}.appendChild(empty_text);
                seq53{n}.innerHTML = "<br><b><u>5'-3' strand</u>:</b><br><font face='courier'>{seq}</font>";
            var seq35{n} = document.createElement('p');
                seq35{n}.appendChild(empty_text);
                seq35{n}.innerHTML = "<br><b><u>3'-5' strand</u>:</b><br><font face='courier'>{seqI}</font>";
            var description{n} = document.createElement('p');
                description{n}.appendChild(empty_text);
                description{n}.innerHTML = "<br><b><u>Description</u>:</b><br>{Desc}"
            var isorf{n} = document.createElement('p');
                isorf{n}.appendChild(empty_text);
                isorf{n}.innerHTML = "<br><b><u>Sequence is orf</u>:</b><br>{orf}"
            var GCcont{n} = document.createElement('p');
                GCcont{n}.appendChild(empty_text);
                GCcont{n}.innerHTML = "<br><b><u>GC content (%)</u>:</b><br>{GC}"
                
            var new{n} = document.createElement('div');
                modal.appendChild(new{n})
                new{n}.id = "mod{counter}_div{n}";
                new{n}.style = "display: none";

            var info_text{n} = document.getElementById('mod{counter}_div{n}');
                info_text{n}.appendChild(fragLen{n});
                info_text{n}.appendChild(seq53{n});
                info_text{n}.appendChild(seq35{n});
                info_text{n}.appendChild(description{n});
                info_text{n}.appendChild(isorf{n});
                info_text{n}.appendChild(GCcont{n});
                        
            c.addEventListener('click', function(evt) {{
                var mousePos = getMousePos(c, evt);
                debugger;
                if (isInside(mousePos,rect{n})) {{
                    require(
                    ["base/js/dialog"], 
                        function(dialog) {{
                            new{n}.style = "display: block";
                            dialog.modal({{
                                title: '{Name}',
                                body: info_text{n},
                                buttons: {{
                                    'Close': {{}}
                                }}
                            }});
                        }}
                    );
                }}
            }}, false);
            
            '''.format(H = self.fragment_height,
                       L = self.normalized_size(Frag),
                       Start = start_x,
                       End = end_x,
                       Mid_y = middle_y,
                       Delta = delta_y,
                       y_in = end_y_in,
                       y_out = end_y_out,
                       P_Ovr = self.frag_list[Frag].left_overlap_size,
                       Ovr = self.overlap_width,
                       Par = Frag%2,
                       C = corner,
                       n = Frag,
                       counter = self.counter,
                       Name = self.frag_list[Frag].name,
                       F_len = len(self.frag_list[Frag]),
                       seq = self.frag_list[Frag].seq.watson,
                       seqI = self.frag_list[Frag].seq.crick[::-1],
                       Desc = self.frag_list[Frag].description,
                       orf = self.frag_list[Frag].isorf(),
                       GC = self.frag_list[Frag].gc())
            
            end_x = start_x + self.normalized_size(Frag)
            
            end_y_out = middle_y - (((-1)**Frag)*(delta_y))+self.fragment_height/2
            if Frag%2 == 1:
                end_y_in = middle_y - (((-1)**Frag)*delta_y)
            elif Frag%2 == 0:
                end_y_in = middle_y - (((-1)**Frag)*(delta_y))+self.fragment_height
        
        
        '''circular products will be represented with a line 
        which connects the overlap between the last and the first fragment'''
        
        if not self.prod.linear:
            start_x = end_x + self.overlap_width
            js = js + '''
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({Start}-({Ovr}-{C}/2), {Mid_y} -(Math.pow(-1,{n})*{Delta})+{C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({Start}-{Ovr}, {Mid_y} -(Math.pow(-1,{n})*{Delta}), {Ovr}-{C}, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {Start} - {Ovr}/2, {Mid_y} -(Math.pow(-1,{n})*{Delta})+{H}/2+5);
            
            ctx.shadowColor="grey";
            
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({Start}-({Ovr}-{C}/2), {Mid_y}-(Math.pow(-1,{n}+1)*{Delta})+{C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({Start}-({Ovr}-{C}/2), {Mid_y}-(Math.pow(-1,{n}+1)*{Delta}), {Ovr}-{C}, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {Start} - {Ovr}/2, {Mid_y} -(Math.pow(-1,{n}+1)*{Delta})+{H}/2+5);
            
            ctx.beginPath();
            ctx.lineWidth = 0.5;
            ctx.setLineDash([5, 6]);
            ctx.moveTo({Start} -{Ovr}, {y_in});
            ctx.lineTo({Start} -{Ovr}, {H}/2 + {Mid_y} -(Math.pow(-1,{n}+1)*{Delta}));
            ctx.stroke();
            ctx.moveTo({Start}, {y_out});
            ctx.lineTo({Start}, {Mid_y} -(Math.pow(-1,{n}+1)*({Delta}+{Par}*{H}-{H}/2)));
            ctx.stroke();
            
            ctx.setLineDash([]);
            
            ctx.shadowColor="grey";
            ctx.lineWidth = {C}/2
            ctx.beginPath();
            ctx.moveTo({Start}, {Mid_y} -(Math.pow(-1,{n}+1)*{Delta})+({H}/2));
            ctx.lineTo({Start} + 20, {Mid_y} -(Math.pow(-1,{n}+1)*{Delta})+({H}/2));
            ctx.lineTo({Start} + 20, {Can_H} - 2*{C});
            ctx.lineTo({Begin_x}-({Ovr}+20), {Can_H} - 2*{C});
            ctx.lineTo({Begin_x}-({Ovr}+20), {Mid_y} + {Delta}+({H}/2));
            ctx.lineTo({Begin_x}-{Ovr}, {Mid_y} + {Delta}+({H}/2));
            ctx.strokeStyle = "#9999ff";
            ctx.stroke();
            
            ctx.lineWidth = {C};
            ctx.strokeStyle = "#f65555"
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({Begin_x}-({Ovr}-{C}/2), {Mid_y} + {Delta} + {C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({Begin_x}-({Ovr}-{C}/2), {Mid_y} + {Delta}, {Ovr}-{C}, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {Begin_x} - {Ovr}/2, {Mid_y} + {Delta} +{H}/2+5);
            
            ctx.beginPath();
            ctx.fillStyle = "#f65555";
            ctx.strokeRect({Begin_x}-({Ovr}-{C}/2), {Begin_y}+{C}/2, {Ovr}-{C}, {H}-{C});
            ctx.shadowColor="transparent";
            ctx.fillRect({Begin_x}-({Ovr}-{C}/2), {Begin_y}, {Ovr}-{C}/2, {H});
            ctx.fillStyle = "black";
            ctx.fillText("{P_Ovr}", {Begin_x}-{Ovr}/2, {Begin_y}+{H}/2+5);
            
            ctx.beginPath();
            ctx.lineWidth = 0.5;
            ctx.setLineDash([5, 6]);
            ctx.moveTo({Begin_x} -{Ovr}, {Begin_y} + {H}/2);
            ctx.lineTo({Begin_x} -{Ovr}, {Mid_y} + {Delta} + {H}/2);
            ctx.stroke();
            ctx.moveTo({Begin_x}, {Begin_y} + {H});
            ctx.lineTo({Begin_x}, {Mid_y} + {Delta}+{H}/2);
            ctx.stroke();
            '''.format(H = self.fragment_height,
                       Can_H = self.height,
                       Start = start_x,
                       Mid_y = middle_y,
                       P_Ovr = self.frag_list[0].left_overlap_size,
                       Ovr = self.overlap_width,
                       Par = (Frag+1)%2,
                       Begin_y = begin_y,
                       Delta = delta_y,
                       y_in = end_y_in,
                       y_out = end_y_out,
                       L = self.fragment_height,
                       n = Frag,
                       Begin_x = begin_x,
                       C = corner)
            
        return js
