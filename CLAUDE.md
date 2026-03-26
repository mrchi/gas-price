# Gas Price Project Instructions

## 开发命令
`python3 -m http.server` - Run local development server

## 部署配置
- Deployment target: GitHub Pages (static site hosting)
- Pure frontend application (no backend runtime required)
- Auto-deploy on push to main branch

## 已实现功能清单
1. ✅ 北京地区92/95/98号汽油价格展示
2. ✅ 成品油价格历史趋势折线图
3. ✅ 涨跌幅颜色标识（红涨绿跌灰持平）
4. ✅ 成品油类型切换显示/隐藏
5. ✅ 布伦特原油当前价格展示
6. ✅ 布伦特原油历史价格趋势展示
7. ✅ 双Y轴支持（成品油：元/升，原油：美元/桶）
8. ✅ 原油价格涨跌幅自动计算
9. ✅ 原油价格显示/隐藏开关

## 数据文件
- `china_gas.json` - 成品油价格数据
- `crude_oil.json` - 布伦特原油价格数据
- 数据通过GitHub Actions自动更新
