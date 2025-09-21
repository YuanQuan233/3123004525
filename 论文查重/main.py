"""
python实现简单论文查重（优化版）
"""

import sys
import argparse
import jieba.analyse
from functools import lru_cache

@lru_cache(maxsize=100)
def get_word_from_article(fname):
    """带缓存的关键词提取"""
    with open(fname, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return jieba.analyse.extract_tags(content, topK=50)

def compute_sim(word_list1, word_list2):
    """计算文章关键词相似度"""
    if not word_list1 or not word_list2:
        return 0.0
    jiaoji = set(word_list1).intersection(set(word_list2))
    bingjie = set(word_list1).union(set(word_list2))
    return round(len(jiaoji) / len(bingjie), 2) if bingjie else 0.0

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='论文查重系统')
    parser.add_argument('source_file', help='原文文件路径')
    parser.add_argument('target_file', help='抄袭版论文文件路径')
    parser.add_argument('output_file', help='答案输出文件路径')

    args = parser.parse_args()

    # 提取论文关键词（带缓存）
    source_words = get_word_from_article(args.source_file)
    target_words = get_word_from_article(args.target_file)

    # 计算相似度
    similarity = compute_sim(source_words, target_words)

    # 输出到文件
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(f"{similarity:.2f}")

    print(f"论文与原论文相似度：{similarity:.2f}")
    print(f"结果已保存到：{args.output_file}")

if __name__ == "__main__":
    import logging
    jieba.setLogLevel(logging.ERROR)
    main()