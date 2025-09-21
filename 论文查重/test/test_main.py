import unittest
import os
import tempfile
from unittest.mock import patch, mock_open

# 导入被测试的函数
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import get_word_from_article, compute_sim


class TestPlagiarismChecker(unittest.TestCase):

    def setUp(self):
        """每个测试前运行，用于准备工作"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """每个测试后运行，用于清理工作"""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_compute_sim_comprehensive(self):
        """全面测试相似度计算"""
        test_cases = [
            # 基本测试
            (['论文', '查重', '系统'], ['论文', '查重', '系统'], 1.0, "完全相同"),
            (['论文', '查重', '系统'], ['音乐', '艺术', '绘画'], 0.0, "完全不同"),

            # 部分匹配测试 - 修正期望值
            (['论文', '查重', '系统'], ['论文', '系统', '算法'], 0.5, "2/4相似"),  # 2相同/4总数
            (['论文', '查重', '系统'], ['论文', '创新', '研究'], 0.2, "1/5相似"),  # 1相同/5总数 ← 修正这里

            # 边界测试
            ([], ['论文'], 0.0, "空列表1"),
            (['论文'], [], 0.0, "空列表2"),
            ([], [], 0.0, "都为空"),

            # 重复词汇测试
            (['论文', '论文', '查重'], ['论文', '查重', '查重'], 1.0, "重复词汇去重"),

            # 更多测试用例
            (['A'], ['A'], 1.0, "单个词相同"),
            (['A'], ['B'], 0.0, "单个词不同"),
            (['A', 'B'], ['A'], 0.5, "2词vs1词, 1相同/2总数"),  # 1/2=0.5
            (['A', 'B', 'C'], ['A', 'D'], 0.25, "3词vs2词, 1相同/4总数"),  # 1/4=0.25
        ]

        for words1, words2, expected, description in test_cases:
            with self.subTest(description=description):
                result = compute_sim(words1, words2)
                self.assertAlmostEqual(result, expected, places=2, msg=description)

    def test_compute_sim_manual_verification(self):
        """手动验证几个关键案例"""
        # 案例1: 3词 vs 3词，1个相同
        result = compute_sim(['A', 'B', 'C'], ['A', 'D', 'E'])
        # 交集: {'A'} = 1
        # 并集: {'A', 'B', 'C', 'D', 'E'} = 5
        # 相似度: 1/5 = 0.2
        self.assertEqual(result, 0.2)

        # 案例2: 3词 vs 2词，1个相同
        result = compute_sim(['A', 'B', 'C'], ['A', 'D'])
        # 交集: {'A'} = 1
        # 并集: {'A', 'B', 'C', 'D'} = 4
        # 相似度: 1/4 = 0.25
        self.assertEqual(result, 0.25)

        # 案例3: 2词 vs 2词，2个相同
        result = compute_sim(['A', 'B'], ['A', 'B'])
        # 交集: {'A', 'B'} = 2
        # 并集: {'A', 'B'} = 2
        # 相似度: 2/2 = 1.0
        self.assertEqual(result, 1.0)

    @patch('builtins.open', mock_open(read_data='这是一篇关于论文查重的测试文本'))
    @patch('jieba.analyse.extract_tags')
    def test_get_word_from_article_mock(self, mock_extract):
        """使用mock测试关键词提取"""
        mock_extract.return_value = ['论文', '查重', '测试', '文本']
        result = get_word_from_article('dummy_path.txt')
        mock_extract.assert_called_once()
        self.assertEqual(result, ['论文', '查重', '测试', '文本'])

    def test_get_word_from_article_integration(self):
        """集成测试：真实文件处理"""
        test_content = "基于深度学习的论文查重系统研究"
        test_file = os.path.join(self.test_dir, 'test_paper.txt')

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        keywords = get_word_from_article(test_file)

        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertTrue(len(keywords) <= 50)


if __name__ == '__main__':
    unittest.main(verbosity=2)