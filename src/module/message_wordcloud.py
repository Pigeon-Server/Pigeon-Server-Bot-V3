from jieba import lcut
from wordcloud import WordCloud


class MessageWordCloud:
    @staticmethod
    def wordcloud(text: str, save_path: str) -> None:
        res = lcut(text)
        counts = {}
        for word in res:
            if len(word) == 1:
                continue
            counts[word] = counts.get(word, 0) + 1
        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)
        words = []
        for i in range(0, 50):
            if i >= len(items):
                break
            word, count = items[i]
            words.append(word)
        text_cut = '/'.join(words)
        wordcloud = WordCloud(background_color='white', font_path='resource/msyh.ttc', width=1000, height=860,
                              margin=2).generate(text_cut)
        wordcloud.to_file(save_path)

