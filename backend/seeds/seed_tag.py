#!/usr/bin/env python3
"""Seed stable tag keys with Japanese display labels and descriptions."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.tag import Tag


TAGS = [
    ("feel-good", "Feel-Good Movie", "観終わったあと、自然と気持ちが明るくなる作品。", "元気をもらえる"),
    ("heartwarming", "Heartwarming", "人の優しさやつながりに、心が温まる作品。", "心が温まる"),
    ("heartbreaking", "Heartbreaking", "胸が締めつけられるほど切なく、涙を誘う作品。", "胸が締めつけられる"),
    ("hilarious", "Hilarious", "思わず声を出して笑ってしまう作品。", "とにかく笑える"),
    ("terrifying", "Terrifying", "観終わったあとまで恐怖が残る作品。", "本気で怖い"),
    ("fun-jump-scares", "Fun Jump Scares", "驚かされる演出を娯楽として楽しめる作品。", "驚きも楽しい"),
    ("meh", "Meh", "悪くはないものの、強い印象は残らなかった作品。", "可もなく不可もなく"),
    ("unclear-payoff", "All That for What?", "大きな展開に対して結末が腑に落ちなかった作品。", "結末に納得できない"),
    ("epic", "Epic", "壮大なスケールと高揚感を味わえる作品。", "壮大で圧倒される"),
    ("cozy-watch", "Cozy Watch", "肩の力を抜いて穏やかに楽しめる作品。", "ほっとして観られる"),
    ("unsettling", "Unsettling", "説明しにくい不穏さが長く残る作品。", "不穏な余韻"),
    ("bittersweet", "Bittersweet", "美しさと切なさが同時に残る作品。", "ほろ苦く切ない"),
    ("mind-blowing", "Mind-Blowing", "発想や展開、映像に強い衝撃を受ける作品。", "衝撃を受けた"),
    ("hidden-gem", "Hidden Gem", "期待以上の魅力があり、もっと知られてほしい作品。", "隠れた良作"),
    ("cult-classic", "Cult Classic", "独特の個性があり、熱心な支持を集める作品。", "熱狂的に愛される"),
    ("must-see", "Must-See", "一度は観てほしいと人に勧めたくなる作品。", "一度は観てほしい"),
    ("nostalgic", "Nostalgia Hit", "懐かしい記憶や感情がよみがえる作品。", "懐かしい気持ち"),
    ("dated", "Hasn't Aged Well", "現在の感覚では気になる表現や価値観がある作品。", "今見ると気になる"),
    ("rewatchable", "Rewatchable", "何度でも観返したくなる作品。", "何度でも観たい"),
    ("masterpiece", "Masterpiece", "演出や物語が高い水準でまとまった傑作。", "文句なしの傑作"),
    ("deeply-satisfying", "I Can Die Now", "大きな満足感で心が満たされる作品。", "満足感がすごい"),
    ("guilty-pleasure", "Guilty Pleasure", "欠点も含めてなぜか好きになってしまう作品。", "欠点も含めて好き"),
    ("silly-fun", "So Stupid It's Good", "ばかばかしさを思い切り楽しめる作品。", "くだらなさが楽しい"),
    ("perfect-for-a-date", "Perfect for a Date", "二人で気軽に楽しみ、感想を共有しやすい作品。", "デートで観たい"),
    ("crowd-pleaser", "Crowd Pleaser", "幅広い人が一緒に楽しみやすい作品。", "みんなで楽しめる"),
    ("family-friendly", "Family Friendly", "世代の違う家族とも観やすい作品。", "家族で観やすい"),
    ("conversation-starter", "Conversation Starter", "観たあとに誰かと語り合いたくなる作品。", "語りたくなる"),
    ("late-night", "Late-Night Watch", "静かな夜にじっくり味わいたい作品。", "夜に観たい"),
    ("underrated", "Underrated", "評価以上の魅力があると感じた作品。", "もっと評価されてほしい"),
    ("overrated", "Overrated", "評判ほどは響かなかった作品。", "評判ほどではない"),
    ("perfect-cast", "Perfect Cast", "配役が役柄にぴったり合っている作品。", "配役がぴったり"),
    ("great-script", "Amazing Script", "台詞や構成、物語の組み立てが優れた作品。", "脚本がすばらしい"),
    ("visual-feast", "Visual Feast", "どの場面も見入ってしまうほど映像が美しい作品。", "映像が美しい"),
    ("great-soundtrack", "Great Soundtrack", "音楽が作品の魅力を大きく高めている作品。", "音楽がすばらしい"),
    ("comfort-movie", "Comfort Movie", "疲れたときに戻ってきたくなる安心できる作品。", "心のよりどころ"),
    ("emotional-damage", "Emotional Damage", "しばらく立ち直れないほど感情を揺さぶる作品。", "感情を揺さぶられた"),
    ("confusing", "What Did I Just Watch?", "理解しきれなくても頭から離れない不思議な作品。", "何を観たのだろう"),
    ("slow-burn", "Slow Burn", "ゆっくり積み上げた先の余韻を楽しむ作品。", "じわじわ効く"),
    ("too-long", "Too Long", "魅力はあるものの、上映時間を長く感じた作品。", "少し長く感じた"),
    ("surprisingly-good", "Surprisingly Good", "予想をよい意味で裏切ってくれた作品。", "予想以上によかった"),
    ("pure-chaos", "Pure Chaos", "混沌とした勢いそのものを楽しめる作品。", "混沌が楽しい"),
    ("badass", "Badass", "人物や見せ場がとにかく格好いい作品。", "とにかく格好いい"),
    ("smart", "Smart and Clever", "緻密な発想や構成に知的な面白さがある作品。", "知的で巧み"),
    ("beautifully-weird", "Beautifully Weird", "奇妙さと美しさが独自の魅力になっている作品。", "美しくて不思議"),
    ("instant-classic", "Instant Classic", "これから長く語り継がれそうな作品。", "新たな定番"),
    ("not-for-me", "Not for Me", "作品の意図は分かるものの、自分には合わなかった作品。", "自分には合わない"),
    ("great-villain", "Great Villain", "敵役の存在感が特に印象に残る作品。", "敵役が魅力的"),
    ("strong-ending", "Strong Ending", "最後の場面が作品全体を力強く締めくくる作品。", "ラストがすばらしい"),
    ("weak-ending", "Weak Ending", "途中は楽しめても、結末に物足りなさが残る作品。", "ラストが惜しい"),
    ("vibe-over-plot", "Vibe Over Plot", "筋書き以上に空気感や世界観を味わう作品。", "物語より雰囲気"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for key, legacy_name, description_ja, display_name_ja in TAGS:
            tag = db.query(Tag).filter(Tag.name == legacy_name).one_or_none()
            if tag is None:
                tag = Tag(
                    key=key,
                    name=legacy_name,
                    description=description_ja,
                    display_name_ja=display_name_ja,
                    description_ja=description_ja,
                )
                db.add(tag)
            else:
                tag.key = key
                tag.display_name_ja = display_name_ja
                tag.description_ja = description_ja
        db.commit()
        print(f"{len(TAGS)}件の日本語タグを登録しました。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
