import seaborn as sns

# Import data from shared.py
#from shared import df

from shiny import App, render, ui

#選択項目
app_ui = ui.page_sidebar(
    ui.sidebar(
        
        ui.input_select(
        "val", "1つ目の項目を選択:", choices=["投票率", "有権者数", "定数比", "有権者数（男女別）"], selected=None
        ),
        ui.input_select(
        "val", "2つ目の項目を選択:", choices=["投票率", "有権者数", "定数比", "有権者数（男女別）"], selected=None
        ),
    ),    
    ui.output_plot("histgram"),
    title="大阪の政治",
)

def server(input, output, session):
    @render.plot
    def histgram():
        hue = "sex" if input.sex() else None
        if input.graph_shapes()=="あらめ":
            sns.displot(df, x=input.val(), hue=hue)
        if input.graph_shapes()=="なめらか":
            sns.kdeplot(df, x=input.val(), hue=hue)
        if input.show_rug():
            sns.rugplot(df, x=input.val(), hue=hue, color="black", alpha=0.25)

app_ui = ui.page_fluid(
    ui.input_slider("slider", "Slider", min=0, max=100, value=[35, 65]),  
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return f"{input.slider()}"

app = App(app_ui, server)

#頭文字検索参考例
from shiny import App, reactive, render, ui
import pandas as pd

sample_data = pd.DataFrame({
    'name': ["池田市", "泉大津市", "泉佐野市", "和泉市", "茨木市", "大阪狭山市", "大阪市",
	"貝塚市", "柏原市", "交野市", "門真市", "河南町", "河内長野市", "岸和田市", "熊取町",
"堺市", "四條畷市", "島本町", "吹田市", "摂津市", "泉南市",
"太子町", "大東市", "高石市", "高槻市", "田尻町", "忠岡町", "千早赤阪村", "豊中市", "豊能町","富田林市",
"寝屋川市", "能勢町",
"羽曳野市", "阪南市","東大阪市", "枚方市", "藤井寺市",
"松原市", "岬町", "箕面市", "守口市",
"八尾市"],#一応あいうえお順です
    'category': ['人名', '果物', '人名', '果物', '人名', '果物', '人名', '果物', '人名', '果物']
})

# データから実際に存在する頭文字を抽出
def get_initial_chars(data):
    initials = set()
    for name in data['name']:
        if name:
            initials.add(name[0])
    return sorted(list(initials))

available_initials = get_initial_chars(sample_data)

app_ui = ui.page_fluid(
    ui.h2("頭文字検索"),
    ui.div(
        ui.h4("利用可能な頭文字:"),
        ui.output_ui("dynamic_buttons"),
        class_="mb-3"
    ),
    ui.div(
        ui.output_text("current_filter"),
        ui.output_text("stats_info"),
        class_="mb-3"
    ),
    ui.card(
        ui.card_header("検索結果"),
        ui.output_table("results")
    )
)

def server(input, output, session):
    selected_initial = reactive.value("")
    
    @render.ui
    def dynamic_buttons():
        buttons = []
        
        # データに存在する各頭文字に対してボタンを生成
        for initial in available_initials:
            count = len(sample_data[sample_data['name'].str.startswith(initial)])
            button_id = f"btn_{ord(initial)}"  # ユニークなIDを生成
            
            # 現在選択されているボタンのスタイルを変更
            current_initial = selected_initial.get()
            button_class = "btn-primary me-2 mb-2" if current_initial == initial else "btn-outline-primary me-2 mb-2"
            
            buttons.append(
                ui.input_action_button(
                    button_id, 
                    f"{initial} ({count}件)",
                    class_=button_class
                )
            )
        
        # すべて表示ボタンのスタイルも動的に変更
        all_button_class = "btn-success me-2 mb-2" if selected_initial.get() == "" else "btn-outline-secondary me-2 mb-2"
        buttons.append(ui.input_action_button("btn_all", "すべて表示", class_=all_button_class))
        return ui.div(*buttons)
    
    # 動的にボタンのクリックイベントを処理
    @reactive.effect
    def _():
        for initial in available_initials:
            button_id = f"btn_{ord(initial)}"
            if hasattr(input, button_id) and getattr(input, button_id)() > 0:
                selected_initial.set(initial)
                break
        
        if hasattr(input, 'btn_all') and input.btn_all() > 0:
            selected_initial.set("")
    
    @render.text
    def current_filter():
        initial = selected_initial.get()
        if initial:
            return f"📍 フィルタ中: 「{initial}」で始まる項目"
        return "📋 すべての項目を表示中"
    
    @render.text
    def stats_info():
        initial = selected_initial.get()
        if not initial:
            total_count = len(sample_data)
            category_counts = sample_data['category'].value_counts()
            return f"総件数: {total_count}件 | " + " | ".join([f"{cat}: {count}件" for cat, count in category_counts.items()])
        else:
            filtered = sample_data[sample_data['name'].str.startswith(initial)]
            category_counts = filtered['category'].value_counts()
            return f"該当件数: {len(filtered)}件 | " + " | ".join([f"{cat}: {count}件" for cat, count in category_counts.items()])
    
    @render.table  
    def results():
        initial = selected_initial.get()
        if not initial:
            return sample_data
        
        return sample_data[sample_data['name'].str.startswith(initial)]

app = App(app_ui, server)
