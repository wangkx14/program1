/**
 * 此脚本用于修复webpack-dev-server错误覆盖层
 * 在开发服务器启动前运行
 */

const fs = require('fs');
const path = require('path');

// 可能的webpack-dev-server客户端覆盖层文件路径
const possiblePaths = [
  path.resolve(__dirname, '../node_modules/webpack-dev-server/client/overlay.js'),
  path.resolve(__dirname, '../node_modules/webpack-dev-server/client/overlay/index.js')
];

// 执行修复函数
function applyFix() {
  console.log('正在尝试修复webpack-dev-server错误覆盖层...');
  
  let fixed = false;
  
  // 尝试找到并修改webpack-dev-server的覆盖层文件
  for (const filePath of possiblePaths) {
    try {
      if (fs.existsSync(filePath)) {
        console.log(`找到覆盖层文件: ${filePath}`);
        
        // 读取原始文件内容
        const originalContent = fs.readFileSync(filePath, 'utf8');
        
        // 检查文件是否已经被修改过
        if (originalContent.includes('// ResizeObserver错误过滤')) {
          console.log('文件已经被修改过，跳过');
          fixed = true;
          continue;
        }
        
        // 修改内容：在显示错误前添加过滤代码
        let modifiedContent = originalContent;
        
        // 查找可能的插入点
        const insertPoints = [
          'function showProblems(',
          'export function createOverlay(',
          'exports.createOverlay = function(',
          'module.exports = function('
        ];
        
        for (const insertPoint of insertPoints) {
          if (modifiedContent.includes(insertPoint)) {
            // 在函数开始处添加过滤代码
            modifiedContent = modifiedContent.replace(
              new RegExp(`(${insertPoint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})([^{]*\\{)`),
              (match, p1, p2) => {
                return `${p1}${p2}
  // ResizeObserver错误过滤 - 自动添加
  if (Array.isArray(problems)) {
    problems = problems.filter(function(problem) {
      return !(problem && problem.message && typeof problem.message === 'string' && 
              (problem.message.includes('ResizeObserver') || 
               problem.message.includes('Maximum update depth')));
    });
    if (problems.length === 0) return null;
  }
`;
              }
            );
            
            console.log(`在 ${insertPoint} 处添加了错误过滤代码`);
            break;
          }
        }
        
        // 保存修改后的文件
        fs.writeFileSync(filePath, modifiedContent, 'utf8');
        console.log(`成功修改文件: ${filePath}`);
        fixed = true;
      }
    } catch (error) {
      console.error(`处理文件 ${filePath} 时出错:`, error);
    }
  }
  
  if (fixed) {
    console.log('成功修复webpack-dev-server错误覆盖层！');
  } else {
    console.log('未找到可修改的webpack-dev-server覆盖层文件，请检查路径');
  }
}

// 执行修复
applyFix(); 