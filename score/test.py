def find_max_sum(matrix):
    m, n = len(matrix), len(matrix[0])

    # 创建一个大小为 m x n 的二维数组 dp，用于保存每个位置的最大和
    dp = [[0] * n for _ in range(m)]

    # 初始化 dp 的第一行和第一列
    dp[0][0] = matrix[0][0]
    for i in range(1, m):
        dp[i][0] = dp[i - 1][0] + matrix[i][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j - 1] + matrix[0][j]

    # 通过动态规划求解 dp 的每个位置的最大和
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]) + matrix[i][j]

    # 返回最右下角位置的最大和
    return dp[m - 1][n - 1]


if __name__ == '__main__':
    data = [[2] * 12] * 12

    matrix = [
        [1, 5, 3, 7],
        [2, 6, 9, 4],
        [8, 1, 0, 2]
    ]
    for i in range(0, 12):
        data[i][i] = 3
    print(find_max_sum(matrix))
